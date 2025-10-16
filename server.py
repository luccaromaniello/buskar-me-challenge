from __future__ import annotations
import os
import time
from dotenv import load_dotenv
from collections.abc import Sequence
from fastapi import FastAPI, HTTPException, Path, Depends
from pydantic import BaseModel, ConfigDict
from typing import ClassVar, Tuple
from sqlalchemy.engine import Row
from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    DeclarativeBase,
)

_ = load_dotenv()

# --- Configuração do banco ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("Variável de ambiente DATABASE_URL não configurada")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# --- Modelos SQLAlchemy ---
class Machine(Base):
    __tablename__ = "machines"  # pyright: ignore[reportUnannotatedClassAttribute]
    id: ClassVar[Column[str]] = Column(String, primary_key=True, index=True)
    name: ClassVar[Column[str]] = Column(String, index=True)
    last_seen: ClassVar[Column[int]] = Column(Integer, index=True)

    commands: Mapped[list["Command"]] = relationship(
        "Command", back_populates="machine"
    )


class Script(Base):
    __tablename__ = "scripts"  # pyright: ignore[reportUnannotatedClassAttribute]
    name: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text)


class Command(Base):
    __tablename__ = "commands"  # pyright: ignore[reportUnannotatedClassAttribute]

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    machine_id: Mapped[str] = mapped_column(String, ForeignKey("machines.id"))
    script_name: Mapped[str] = mapped_column(String, ForeignKey("scripts.name"))
    status: Mapped[str] = mapped_column(
        String, default="pending"
    )  # "pending" ou "completed"
    output: Mapped[str | None] = mapped_column(Text, nullable=True)

    machine: Mapped["Machine"] = relationship("Machine", back_populates="commands")
    script: Mapped["Script"] = relationship("Script")


# --- Schemas Pydantic ---
class MachineCreate(BaseModel):
    id: str
    name: str


class MachineSchema(BaseModel):
    id: str
    name: str
    last_seen: int

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


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

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class CommandWithContentSchema(BaseModel):
    id: int
    machine_id: str
    script_name: str
    script_content: str
    status: str
    output: str | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


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
@app.get("/machines", response_model=list[MachineSchema])
def get_machines():
    """
    Retorna máquinas ativas que pingaram nos últimos 5 minutos.
    """
    db = next(get_db())
    cutoff = int(time.time()) - 300  # 5 minutos em segundos
    machines = db.query(Machine).filter(Machine.last_seen >= cutoff).all()
    return machines


@app.post("/register_machine")
def register_machine(machine: MachineCreate):
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


def get_machine_id(machine_id: str = Path(..., description="ID da máquina")):
    return machine_id


@app.get("/commands/{machine_id}", response_model=list[CommandWithContentSchema])
def get_commands(
    machine_id: str = Depends(get_machine_id),
) -> list[CommandWithContentSchema]:
    db = next(get_db())

    results: Sequence[Row[Tuple[Command, Script]]] = (
        db.query(Command, Script)
        .join(Script, Command.script_name == Script.name)
        .filter(Command.machine_id == machine_id, Command.status == "pending")
        .all()
    )

    commands_with_content: list[CommandWithContentSchema] = []
    for row in results:
        cmd: Command = row[0]
        script: Script = row[1]
        commands_with_content.append(
            CommandWithContentSchema(
                id=cmd.id,
                machine_id=cmd.machine_id,
                script_name=cmd.script_name,
                script_content=script.content,
                status=cmd.status,
                output=cmd.output,
            )
        )
    return commands_with_content


@app.post("/commands/{command_id}/result")
def post_command_result(command_id: int, result: CommandResultSchema):
    """
    Recebe o resultado da execução do comando (chamado pelo agente).
    """
    db = next(get_db())
    command = db.query(Command).filter(Command.id == command_id).first()
    if not command:
        raise HTTPException(status_code=404, detail="Comando não encontrado")

    command.output = result.output
    command.status = "completed"
    db.commit()
    return {"message": "Resultado do comando salvo com sucesso"}
