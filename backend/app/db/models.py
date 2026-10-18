from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    numero_cuenta = Column(String, unique=True, nullable=False)


class Cuenta(Base):
    __tablename__ = "cuentas"
    id = Column(Integer, primary_key=True)
    numero_cuenta = Column(String, unique=True, nullable=False)
    titular = Column(String, nullable=False)
    saldo = Column(Numeric(12, 2), nullable=False, default=0)
    limite_diario = Column(Numeric(12, 2), nullable=False, default=2000)


class Transaccion(Base):
    __tablename__ = "transacciones"
    id = Column(Integer, primary_key=True)
    cuenta_origen = Column(String, nullable=False)
    cuenta_destino = Column(String, nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    concepto = Column(String, nullable=True)
    canal_origen = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class InteractionLog(Base):
    __tablename__ = "interaction_logs"
    id = Column(Integer, primary_key=True)
    escenario = Column(String, nullable=False)
    cadena_id = Column(String, nullable=True)
    tecnica = Column(String, nullable=True)
    session_id = Column(String, nullable=False)
    user_input = Column(String, nullable=False)
    llm_raw_response = Column(JSON, nullable=True)
    function_called = Column(String, nullable=True)
    function_args = Column(JSON, nullable=True)
    function_result = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    descuento_pct = Column(Numeric(5, 2), nullable=False, default=0)


class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario_aplicado = Column(Numeric(10, 2), nullable=False)
    cliente = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Resena(Base):
    __tablename__ = "resenas"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, nullable=False)
    autor = Column(String, nullable=False)
    texto = Column(String, nullable=False)
    estrellas = Column(Integer, nullable=False, default=5)


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    cliente = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    estado = Column(String, nullable=False, default="abierto")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ConfiguracionInterna(Base):
    __tablename__ = "configuracion_interna"
    id = Column(Integer, primary_key=True)
    clave = Column(String, nullable=False)
    valor = Column(String, nullable=False)


class Agente(Base):
    __tablename__ = "agentes"
    id = Column(Integer, primary_key=True)
    usuario = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    numero_historia = Column(String, unique=True, nullable=False)


class HistorialMedico(Base):
    __tablename__ = "historial_medico"
    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, nullable=False)
    numero_historia = Column(String, nullable=False)
    diagnostico = Column(String, nullable=False)
    notas = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
