import pytest
from fastapi import HTTPException
from app.services.project_service import (
    crear_proyecto,
    get_proyecto,
    get_proyectos,
    update_proyecto,
    eliminar_proyecto
)
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.user import User
from app.core.security import hash_password


# ─── FIXTURE — usuario de prueba ─────────────────────────────

@pytest.fixture
def usuario_prueba(db):
    """
    Crea un usuario real en la BD de pruebas
    para usarlo como dueño de los proyectos
    """
    user = User(
        nombre_completo="Test User",
        correo="test@example.com",
        password=hash_password("Test123!"),
        activo=True,
        refresh_token=None
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def proyecto_prueba(db, usuario_prueba):
    """
    Crea un proyecto real en la BD de pruebas
    """
    from app.models.project import Project, OrigenEnum
    proyecto = Project(
        nombre="Proyecto Test",
        origen=OrigenEnum.carga_directa,
        url_github=None,
        usuario_id=usuario_prueba.id
    )
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto


# ─── CREAR PROYECTO ──────────────────────────────────────────

class TestCrearProyecto:

    def test_crear_proyecto_exitoso(self, db, usuario_prueba):
        """Crear proyecto con datos válidos debe guardarlo en BD"""
        data = ProjectCreate(
            nombre="Mi API Flask",
            origen="carga_directa"
        )
        resultado = crear_proyecto(db, data, usuario_prueba)
        assert resultado.nombre == "Mi API Flask"
        assert resultado.usuario_id == usuario_prueba.id
        assert resultado.estado is True   # activo por defecto

    def test_crear_proyecto_con_url_github(self, db, usuario_prueba):
        """Crear proyecto con URL de GitHub debe guardarla"""
        data = ProjectCreate(
            nombre="Repo GitHub",
            origen="github",
            url_github="https://github.com/usuario/repo"
        )
        resultado = crear_proyecto(db, data, usuario_prueba)
        assert resultado.url_github == "https://github.com/usuario/repo"
        assert resultado.origen == "github"

    def test_crear_proyecto_sin_nombre_falla(self, db, usuario_prueba):
        """Crear proyecto sin nombre debe fallar con validación"""
        with pytest.raises(Exception):
            ProjectCreate(origen="carga_directa")  # nombre es requerido


# ─── LISTAR PROYECTOS ────────────────────────────────────────

class TestListarProyectos:

    def test_listar_proyectos_vacios(self, db, usuario_prueba):
        """Usuario sin proyectos debe recibir lista vacía"""
        resultado = get_proyectos(db, usuario_prueba)
        assert resultado["total"] == 0
        assert resultado["proyectos"] == []

    def test_listar_proyectos_del_usuario(self, db, usuario_prueba, proyecto_prueba):
        """Usuario con proyectos debe verlos en su lista"""
        resultado = get_proyectos(db, usuario_prueba)
        assert resultado["total"] == 1
        assert resultado["proyectos"][0].nombre == "Proyecto Test"

    def test_usuario_solo_ve_sus_proyectos(self, db, usuario_prueba):
        """Un usuario no debe ver proyectos de otro usuario"""
        # Crea un segundo usuario
        otro_usuario = User(
            nombre_completo="Otro User",
            correo="otro@example.com",
            password=hash_password("Test123!"),
            activo=True,
            refresh_token=None
        )
        db.add(otro_usuario)
        db.commit()
        db.refresh(otro_usuario)

        # Crea proyecto del segundo usuario
        from app.models.project import Project, OrigenEnum
        proyecto_ajeno = Project(
            nombre="Proyecto Ajeno",
            origen=OrigenEnum.carga_directa,
            usuario_id=otro_usuario.id
        )
        db.add(proyecto_ajeno)
        db.commit()

        # usuario_prueba no debe ver el proyecto ajeno
        resultado = get_proyectos(db, usuario_prueba)
        assert resultado["total"] == 0


# ─── VER UN PROYECTO ─────────────────────────────────────────

class TestVerProyecto:

    def test_ver_proyecto_exitoso(self, db, usuario_prueba, proyecto_prueba):
        """Ver proyecto propio debe devolverlo correctamente"""
        resultado = get_proyecto(db, proyecto_prueba.id, usuario_prueba)
        assert resultado.id == proyecto_prueba.id
        assert resultado.nombre == "Proyecto Test"

    def test_ver_proyecto_inexistente(self, db, usuario_prueba):
        """Ver proyecto que no existe debe devolver 404"""
        with pytest.raises(HTTPException) as exc:
            get_proyecto(db, 9999, usuario_prueba)
        assert exc.value.status_code == 404

    def test_ver_proyecto_ajeno(self, db, usuario_prueba):
        """Ver proyecto de otro usuario debe devolver 403"""
        # Crea otro usuario con su proyecto
        otro_usuario = User(
            nombre_completo="Otro User",
            correo="otro2@example.com",
            password=hash_password("Test123!"),
        )
        db.add(otro_usuario)
        db.commit()
        db.refresh(otro_usuario)

        from app.models.project import Project, OrigenEnum
        proyecto_ajeno = Project(
            nombre="Proyecto Ajeno",
            origen=OrigenEnum.carga_directa,
            usuario_id=otro_usuario.id
        )
        db.add(proyecto_ajeno)
        db.commit()
        db.refresh(proyecto_ajeno)

        # usuario_prueba intenta ver el proyecto ajeno
        with pytest.raises(HTTPException) as exc:
            get_proyecto(db, proyecto_ajeno.id, usuario_prueba)
        assert exc.value.status_code == 403


# ─── ACTUALIZAR PROYECTO ─────────────────────────────────────

class TestActualizarProyecto:

    def test_actualizar_nombre(self, db, usuario_prueba, proyecto_prueba):
        """Actualizar nombre debe reflejarse en BD"""
        data = ProjectUpdate(nombre="Nuevo Nombre")
        resultado = update_proyecto(db, proyecto_prueba.id, data, usuario_prueba)
        assert resultado.nombre == "Nuevo Nombre"

    def test_actualizar_url_github(self, db, usuario_prueba, proyecto_prueba):
        """Actualizar URL de GitHub debe guardarse"""
        data = ProjectUpdate(url_github="https://github.com/nuevo/repo")
        resultado = update_proyecto(db, proyecto_prueba.id, data, usuario_prueba)
        assert resultado.url_github == "https://github.com/nuevo/repo"

    def test_actualizar_proyecto_ajeno(self, db, usuario_prueba):
        """Actualizar proyecto ajeno debe devolver 403"""
        otro_usuario = User(
            nombre_completo="Otro User",
            correo="otro3@example.com",
            password=hash_password("Test123!"),
            activo=True,
            refresh_token=None
        )
        db.add(otro_usuario)
        db.commit()
        db.refresh(otro_usuario)

        from app.models.project import Project, OrigenEnum
        proyecto_ajeno = Project(
            nombre="Ajeno",
            origen=OrigenEnum.carga_directa,
            usuario_id=otro_usuario.id
        )
        db.add(proyecto_ajeno)
        db.commit()
        db.refresh(proyecto_ajeno)

        data = ProjectUpdate(nombre="Intento hackear")
        with pytest.raises(HTTPException) as exc:
            update_proyecto(db, proyecto_ajeno.id, data, usuario_prueba)
        assert exc.value.status_code == 403


# ─── ELIMINAR PROYECTO ───────────────────────────────────────

class TestEliminarProyecto:

    def test_eliminar_proyecto_exitoso(self, db, usuario_prueba, proyecto_prueba):
        """Eliminar proyecto debe marcarlo como inactivo"""
        resultado = eliminar_proyecto(db, proyecto_prueba.id, usuario_prueba)
        assert resultado["message"] is not None

        # Verificar que ya no aparece en la lista
        lista = get_proyectos(db, usuario_prueba)
        assert lista["total"] == 0

    def test_eliminar_proyecto_inexistente(self, db, usuario_prueba):
        """Eliminar proyecto que no existe debe devolver 404"""
        with pytest.raises(HTTPException) as exc:
            eliminar_proyecto(db, 9999, usuario_prueba)
        assert exc.value.status_code == 404

    def test_eliminar_proyecto_ajeno(self, db, usuario_prueba):
        """Eliminar proyecto ajeno debe devolver 403"""
        otro_usuario = User(
            nombre_completo="Otro User",
            correo="otro4@example.com",
            password=hash_password("Test123!"),
            activo=True,
            refresh_token=None
        )
        db.add(otro_usuario)
        db.commit()
        db.refresh(otro_usuario)

        from app.models.project import Project, OrigenEnum
        proyecto_ajeno = Project(
            nombre="Ajeno",
            origen=OrigenEnum.carga_directa,
            usuario_id=otro_usuario.id
        )
        db.add(proyecto_ajeno)
        db.commit()
        db.refresh(proyecto_ajeno)

        with pytest.raises(HTTPException) as exc:
            eliminar_proyecto(db, proyecto_ajeno.id, usuario_prueba)
        assert exc.value.status_code == 403