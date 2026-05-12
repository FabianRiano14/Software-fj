# Sistema de gestion de clientes, servicios y reservas
# Empresa: Software FJ
# Curso: Programacion 213023 - UNAD
# Estudiante: Edwin Fabian Riaño Sanchez

import logging
from abc import ABC, abstractmethod
from datetime import datetime

# configurar el archivo de logs
logging.basicConfig(
    filename="errores_log.txt",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---- Excepciones personalizadas ----

class ErrorDatos(Exception):
    # error cuando los datos ingresados son incorrectos
    pass

class ErrorServicio(Exception):
    # error cuando el servicio no esta disponible o es invalido
    pass

class ErrorReserva(Exception):
    # error cuando la reserva no se puede realizar
    pass


# ---- Clase abstracta base ----

class Entidad(ABC):
    # clase base para todas las entidades del sistema
    contador = 0

    def __init__(self, nombre):
        Entidad.contador += 1
        self.id = Entidad.contador
        self.nombre = nombre

    @abstractmethod
    def mostrar_info(self):
        pass


# ---- Clase Cliente ----

class Cliente(Entidad):

    def __init__(self, nombre, email, telefono):
        super().__init__(nombre)
        # validar nombre
        if not nombre or len(nombre) < 3:
            raise ErrorDatos("El nombre debe tener al menos 3 caracteres")
        # validar email basico
        if "@" not in email or "." not in email:
            raise ErrorDatos("El email no es valido")
        # validar telefono
        if not telefono.isdigit() or len(telefono) < 7:
            raise ErrorDatos("El telefono debe tener minimo 7 digitos")

        self.__nombre = nombre
        self.__email = email
        self.__telefono = telefono

    # getters encapsulados
    def get_nombre(self):
        return self.__nombre

    def get_email(self):
        return self.__email

    def get_telefono(self):
        return self.__telefono

    def mostrar_info(self):
        return f"Cliente {self.id}: {self.__nombre} | {self.__email} | Tel: {self.__telefono}"


# ---- Clase abstracta Servicio ----

class Servicio(Entidad, ABC):

    def __init__(self, nombre, precio_hora):
        super().__init__(nombre)
        if precio_hora <= 0:
            raise ErrorServicio("El precio debe ser mayor a cero")
        self.precio_hora = precio_hora
        self.disponible = True

    @abstractmethod
    def calcular_costo(self, horas):
        pass

    @abstractmethod
    def describir(self):
        pass

    def mostrar_info(self):
        estado = "disponible" if self.disponible else "no disponible"
        return f"Servicio {self.id}: {self.nombre} | ${self.precio_hora}/hora | {estado}"


# ---- Servicio 1: Sala de reunion ----

class SalaReunion(Servicio):

    def __init__(self, nombre, precio_hora, capacidad):
        super().__init__(nombre, precio_hora)
        if capacidad <= 0:
            raise ErrorServicio("La capacidad debe ser mayor a cero")
        self.capacidad = capacidad

    def calcular_costo(self, horas, descuento=0):
        # calculo con descuento opcional - metodo sobrecargado
        if descuento < 0 or descuento > 100:
            raise ErrorDatos("El descuento debe estar entre 0 y 100")
        total = self.precio_hora * horas
        total = total - (total * descuento / 100)
        return round(total, 2)

    def describir(self):
        return f"Sala de reunion: {self.nombre} | Capacidad: {self.capacidad} personas"

    def mostrar_info(self):
        return f"{self.describir()} | ${self.precio_hora}/hora"


# ---- Servicio 2: Alquiler de equipo ----

class AlquilerEquipo(Servicio):

    def __init__(self, nombre, precio_hora, tipo_equipo):
        super().__init__(nombre, precio_hora)
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, horas, cantidad=1):
        # calculo con cantidad de equipos opcional - metodo sobrecargado
        if cantidad <= 0:
            raise ErrorDatos("La cantidad debe ser mayor a cero")
        total = self.precio_hora * horas * cantidad
        return round(total, 2)

    def describir(self):
        return f"Equipo: {self.nombre} | Tipo: {self.tipo_equipo}"

    def mostrar_info(self):
        return f"{self.describir()} | ${self.precio_hora}/hora"


# ---- Servicio 3: Asesoria especializada ----

class Asesoria(Servicio):

    def __init__(self, nombre, precio_hora, area):
        super().__init__(nombre, precio_hora)
        if not area:
            raise ErrorServicio("El area de asesoria no puede estar vacia")
        self.area = area

    def calcular_costo(self, horas, sesiones=1):
        # calculo con numero de sesiones opcional - metodo sobrecargado
        if sesiones <= 0:
            raise ErrorDatos("El numero de sesiones debe ser mayor a cero")
        total = self.precio_hora * horas * sesiones
        return round(total, 2)

    def describir(self):
        return f"Asesoria en: {self.area} | Asesor: {self.nombre}"

    def mostrar_info(self):
        return f"{self.describir()} | ${self.precio_hora}/hora"


# ---- Clase Reserva ----

class Reserva:

    def __init__(self, cliente, servicio, horas):
        if not isinstance(cliente, Cliente):
            raise ErrorReserva("El cliente no es valido")
        if not isinstance(servicio, Servicio):
            raise ErrorReserva("El servicio no es valido")
        if horas <= 0:
            raise ErrorReserva("Las horas deben ser mayor a cero")
        if not servicio.disponible:
            raise ErrorReserva(f"El servicio '{servicio.nombre}' no esta disponible")

        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "pendiente"
        self.costo = 0
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    def confirmar(self, **kwargs):
        # try/except/else para confirmar y calcular costo
        try:
            if self.estado != "pendiente":
                raise ErrorReserva("Solo se pueden confirmar reservas pendientes")
            self.costo = self.servicio.calcular_costo(self.horas, **kwargs)
        except ErrorDatos as e:
            raise ErrorReserva(f"Error calculando el costo: {e}") from e
        else:
            # solo se ejecuta si no hubo error
            self.estado = "confirmada"
            print(f"  Reserva confirmada. Costo total: ${self.costo:,.0f}")

    def cancelar(self):
        # try/except/finally para cancelar
        try:
            if self.estado == "cancelada":
                raise ErrorReserva("La reserva ya esta cancelada")
            self.estado = "cancelada"
            print(f"  Reserva cancelada.")
        except ErrorReserva:
            raise
        finally:
            pass  # siempre se ejecuta

    def mostrar_info(self):
        return (f"Reserva | Cliente: {self.cliente.get_nombre()} | "
                f"Servicio: {self.servicio.nombre} | "
                f"Horas: {self.horas} | Estado: {self.estado} | "
                f"Costo: ${self.costo:,.0f}")


# ---- Sistema principal ----

class SistemaFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def agregar_cliente(self, nombre, email, telefono):
        try:
            c = Cliente(nombre, email, telefono)
            self.clientes.append(c)
            print(f"  OK - {c.mostrar_info()}")
            return c
        except ErrorDatos as e:
            logging.error(f"Error al registrar cliente '{nombre}': {e}")
            print(f"  ERROR: {e}")
            return None
        finally:
            pass  # bloque finally, siempre se ejecuta

    def agregar_servicio(self, servicio):
        try:
            self.servicios.append(servicio)
            print(f"  OK - {servicio.mostrar_info()}")
            return servicio
        except Exception as e:
            logging.error(f"Error al agregar servicio: {e}")
            print(f"  ERROR: {e}")
            return None

    def hacer_reserva(self, cliente, servicio, horas):
        try:
            r = Reserva(cliente, servicio, horas)
            self.reservas.append(r)
            print(f"  Reserva creada para {cliente.get_nombre()} - {servicio.nombre}")
            return r
        except ErrorReserva as e:
            logging.error(f"Error al crear reserva: {e}")
            print(f"  ERROR: {e}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado: {e}")
            print(f"  ERROR inesperado: {e}")
            return None
        finally:
            pass  # siempre se ejecuta

    def listar_todo(self):
        print("\n--- Clientes registrados ---")
        for c in self.clientes:
            print(" ", c.mostrar_info())
        print("\n--- Servicios ---")
        for s in self.servicios:
            print(" ", s.mostrar_info())
        print("\n--- Reservas ---")
        for r in self.reservas:
            print(" ", r.mostrar_info())


# ---- Simulacion de operaciones ----

def main():
    print("=" * 50)
    print("  SISTEMA SOFTWARE FJ - GESTION DE RESERVAS")
    print("=" * 50)

    sistema = SistemaFJ()

    # Operacion 1: cliente valido
    print("\n[Op 1] Registrar cliente valido")
    c1 = sistema.agregar_cliente("Juan Perez", "juan@gmail.com", "3001234567")

    # Operacion 2: otro cliente valido
    print("\n[Op 2] Registrar otro cliente")
    c2 = sistema.agregar_cliente("Maria Lopez", "maria@empresa.com", "6014567890")

    # Operacion 3: email invalido
    print("\n[Op 3] Cliente con email invalido")
    c3 = sistema.agregar_cliente("Carlos Ruiz", "correo_sin_arroba", "3009876543")

    # Operacion 4: nombre muy corto
    print("\n[Op 4] Cliente con nombre muy corto")
    c4 = sistema.agregar_cliente("AB", "ab@email.com", "3001111111")

    # Operacion 5: crear servicios validos
    print("\n[Op 5] Crear servicios")
    sala = equipo = asesoria = None
    try:
        sala = SalaReunion("Sala A", 50000, 10)
        sistema.agregar_servicio(sala)

        equipo = AlquilerEquipo("Proyector Epson", 30000, "proyector")
        sistema.agregar_servicio(equipo)

        asesoria = Asesoria("Luis Gomez", 80000, "Redes y Seguridad")
        sistema.agregar_servicio(asesoria)
    except ErrorServicio as e:
        logging.error(f"Error creando servicio: {e}")
        print(f"  ERROR: {e}")

    # Operacion 6: servicio con precio invalido
    print("\n[Op 6] Servicio con precio invalido")
    try:
        sala_mala = SalaReunion("Sala B", -1000, 5)
        sistema.agregar_servicio(sala_mala)
    except ErrorServicio as e:
        logging.error(f"Error servicio invalido: {e}")
        print(f"  ERROR esperado: {e}")

    # Operacion 7: reserva valida con sala
    print("\n[Op 7] Reserva valida - sala")
    r1 = None
    if c1 and sala:
        r1 = sistema.hacer_reserva(c1, sala, 3)
        if r1:
            try:
                r1.confirmar(descuento=10)
            except ErrorReserva as e:
                logging.error(f"Error confirmando: {e}")
                print(f"  ERROR: {e}")

    # Operacion 8: reserva de asesoria
    print("\n[Op 8] Reserva valida - asesoria")
    r2 = None
    if c2 and asesoria:
        r2 = sistema.hacer_reserva(c2, asesoria, 2)
        if r2:
            try:
                r2.confirmar(sesiones=2)
            except ErrorReserva as e:
                logging.error(f"Error: {e}")
                print(f"  ERROR: {e}")

    # Operacion 9: servicio no disponible
    print("\n[Op 9] Reservar servicio no disponible")
    if sala:
        sala.disponible = False
        r3 = sistema.hacer_reserva(c1, sala, 2)
        sala.disponible = True  # volver a activar

    # Operacion 10: descuento invalido
    print("\n[Op 10] Confirmar con descuento invalido")
    r4 = None
    if c1 and equipo:
        r4 = sistema.hacer_reserva(c1, equipo, 4)
        if r4:
            try:
                r4.confirmar(cantidad=-5)
            except ErrorReserva as e:
                logging.error(f"Error descuento invalido: {e}")
                print(f"  ERROR esperado: {e}")

    # Operacion 11: cancelar reserva
    print("\n[Op 11] Cancelar reserva")
    if r2:
        try:
            r2.cancelar()
        except ErrorReserva as e:
            logging.error(f"Error al cancelar: {e}")
            print(f"  ERROR: {e}")

    # Operacion 12: cancelar reserva ya cancelada
    print("\n[Op 12] Cancelar reserva ya cancelada")
    if r2:
        try:
            r2.cancelar()
        except ErrorReserva as e:
            logging.error(f"Error cancelacion doble: {e}")
            print(f"  ERROR esperado: {e}")

    # mostrar resumen final
    sistema.listar_todo()

    print("\n" + "=" * 50)
    print("Fin. Revise errores_log.txt para ver los errores.")
    print("=" * 50)


if __name__ == "__main__":
    main()
