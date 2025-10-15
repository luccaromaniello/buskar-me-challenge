import os
import time
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# --- Configuração do banco ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("Variável de ambiente DATABASE_URL não configurada")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modelos SQLAlchemy ---


class Machine(Base):
    __tablename__ = "machines"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    last_seen = Column(Integer, index=True)

    commands = relationship("Command", back_populates="machine")


class Script(Base):
    __tablename__ = "scripts"
    name = Column(String, primary_key=True, index=True)
    content = Column(Text)


class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    machine_id = Column(String, ForeignKey("machines.id"))
    script_name = Column(String, ForeignKey("scripts.name"))
    status = Column(String, default="pending")  # pending ou completed
    output = Column(Text, nullable=True)

    machine = relationship("Machine", back_populates="commands")
    script = relationship("Script")


# --- Schemas Pydantic ---


class MachineSchema(BaseModel):
    id: str
    name: str
    last_seen: int

    class Config:
        orm_mode = True


class ScriptCreateSchema(BaseModel):
    name: str
    content: str


class CommandCreateSchema(BaseModel):
    machine_id: str
    script_name: str


class CommandSchema(BaseModel):
    id: int
    machine_id: str
    script_name: str
    status: str
    output: str | None = None

    class Config:
        orm_mode = True


class CommandResultSchema(BaseModel):
    output: str


# --- FastAPI app ---

app = FastAPI(title="Gerenciamento Remoto Linux via Discord")


# --- Helpers ---


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Cria as tabelas no banco (execução única no start) ---
Base.metadata.create_all(bind=engine)

# --- Endpoints ---


@app.get("/machines", response_model=List[MachineSchema])
def get_machines():
    """
    Retorna máquinas ativas que pingaram nos últimos 5 minutos.
    """
    db = next(get_db())
    cutoff = int(time.time()) - 300  # 5 minutos em segundos
    machines = db.query(Machine).filter(Machine.last_seen >= cutoff).all()
    return machines


@app.post("/register_machine")
def register_machine(machine: MachineSchema):
    """
    Registra ou atualiza uma máquina (chamado pelo agente).
    """
    db = next(get_db())
    db_machine = db.query(Machine).filter(Machine.id == machine.id).first()
    if db_machine:
        db_machine.name = machine.name  # pyright: ignore[reportAttributeAccessIssue]
        db_machine.last_seen = int(time.time())  # pyright: ignore[reportAttributeAccessIssue]
    else:
        new_machine = Machine(
            id=machine.id, name=machine.name, last_seen=int(time.time())
        )
        db.add(new_machine)
    db.commit()
    return {"message": "Máquina registrada com sucesso"}


@app.post("/scripts")
def register_script(script: ScriptCreateSchema):
    """
    Cadastra um script novo (chamado pelo bot).
    """
    db = next(get_db())
    exists = db.query(Script).filter(Script.name == script.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Script com esse nome já existe")
    new_script = Script(name=script.name, content=script.content)
    db.add(new_script)
    db.commit()
    return {"message": "Script cadastrado com sucesso"}


@app.post("/execute")
def execute_script(cmd: CommandCreateSchema):
    """
    Agenda execução de script em máquina (chamado pelo bot).
    """
    db = next(get_db())
    machine = db.query(Machine).filter(Machine.id == cmd.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    script = db.query(Script).filter(Script.name == cmd.script_name).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script não encontrado")

    command = Command(
        machine_id=cmd.machine_id, script_name=cmd.script_name, status="pending"
    )
    db.add(command)
    db.commit()
    return {"message": f"Comando agendado para máquina {cmd.machine_id}"}


@app.get("/commands/{machine_id}", response_model=list[CommandSchema])
def get_commands(machine_id: str = Path(..., description="ID da máquina")):  # pyright: ignore[reportCallInDefaultInitializer]
    """
    Retorna comandos pendentes para o agente executar.
    """
    db = next(get_db())
    commands = (
        db.query(Command)
        .filter(Command.machine_id == machine_id, Command.status == "pending")
        .all()
    )
    return commands


@app.post("/commands/{command_id}/result")
def post_command_result(command_id: int, result: CommandResultSchema):
    """
    Recebe o resultado da execução do comando (chamado pelo agente).
    """
    db = next(get_db())
    command = db.query(Command).filter(Command.id == command_id).first()
    if not command:
        raise HTTPException(status_code=404, detail="Comando não encontrado")

    command.output = result.output  # pyright: ignore[reportAttributeAccessIssue]
    command.status = "completed"  # pyright: ignore[reportAttributeAccessIssue]
    db.commit()
    return {"message": "Resultado do comando salvo com sucesso"}
