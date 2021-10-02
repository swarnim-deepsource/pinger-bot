"""
Файл для теста датабазы
"""

from database import PostgresController
from pytest import fixture, mark


@fixture(scope='session')
async def database(event_loop):
    """Инициализирует датабазу"""
    db = await PostgresController.get_instance()
    await db.pool.execute("DROP TABLE IF EXISTS sunpings;")
    await db.pool.execute("DROP TABLE IF EXISTS sunservers;")
    yield db
    await db.pool.execute("DROP TABLE IF EXISTS sunpings;")
    await db.pool.execute("DROP TABLE IF EXISTS sunservers;")


class TestAddFunctions:
    """Класс для тестов add_* функций"""

    @mark.asyncio
    async def test_add_server(self, database):
        """Проверяет функцию add_server"""
        await database.make_tables()
        await database.add_server('127.0.0.10', 0, 25565)
        server = await database.pool.fetch("SELECT * FROM sunservers WHERE numip='127.0.0.10' AND port=25565")
        assert len(server) > 0

    @mark.asyncio
    async def test_add_server_owner_id(self, database):
        """Проверяет функцию add_server, правильно ли записывает owner_id"""
        await database.make_tables()
        await database.add_server('127.0.0.11', 123123, 25565)
        server = await database.pool.fetch("SELECT * FROM sunservers WHERE numip='127.0.0.11' AND port=25565")
        assert server[0]['owner'] == 123123

    @mark.asyncio
    async def test_add_ping(self, database):
        """Проверяет функцию add_ping"""
        await database.make_tables()
        await database.add_ping('127.0.0.12', 25565, 33)
        ping = await database.pool.fetch("SELECT * FROM sunpings WHERE ip='127.0.0.12' AND port=25565")
        assert ping[0]['players'] == 33

    @mark.asyncio
    async def test_add_alias(self, database):
        """Проверяет функцию add_alias"""
        await database.make_tables()
        await database.add_server('127.0.0.13', 0, 25565)
        await database.add_alias('тест', '127.0.0.13', 25565)
        server = await database.pool.fetch("SELECT * FROM sunservers WHERE numip='127.0.0.13' AND port=25565")
        assert server[0]['alias'] == 'тест'

    @mark.asyncio
    async def test_add_record(self, database):
        """Проверяет функцию add_record"""
        await database.make_tables()
        await database.add_server('127.0.0.14', 0, 25565)
        await database.add_record('127.0.0.14', 25565, 33)
        server = await database.pool.fetch("SELECT * FROM sunservers WHERE numip='127.0.0.14' AND port=25565")
        assert server[0]['record'] == 33


class TestGetFunctions:
    """Класс для тестов get_* функций"""

    @mark.asyncio
    async def test_get_server(self, database):
        """Проверяет функцию get_server"""
        await database.make_tables()
        await database.add_server('127.0.0.15', 0, 25565)
        answer = await database.get_server('127.0.0.15', 25565)
        right_answer = await database.pool.fetch("SELECT * FROM sunservers WHERE numip='127.0.0.15' AND port=25565")
        assert answer == right_answer

    @mark.asyncio
    async def test_get_servers(self, database):
        """Проверяет функцию get_servers"""
        await database.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await database.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await database.make_tables()
        await database.add_server('127.0.0.16', 0, 25565)
        await database.add_server('127.0.0.17', 0, 25565)
        await database.add_server('127.0.0.18', 0, 25565)
        answer = await database.get_servers()
        right_answer = await database.pool.fetch("SELECT * FROM sunservers;")
        assert answer == right_answer

    @mark.asyncio
    async def test_get_servers_len(self, database):
        """Проверяет функцию get_servers_len"""
        await database.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await database.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await database.make_tables()
        await database.add_server('127.0.0.19', 0, 25565)
        await database.add_server('127.0.0.20', 0, 25565)
        await database.add_server('127.0.0.21', 0, 25565)
        answer = await database.get_servers()
        assert len(answer) == 3

    @mark.asyncio
    async def test_get_ip_alias(self, database):
        """Проверяет функцию get_ip_alias"""
        await database.make_tables()
        await database.add_server('127.0.0.22', 0, 25565)
        await database.add_alias('тест123', '127.0.0.22', 25565)
        answer = await database.get_ip_alias('тест123')
        right_answer = await database.pool.fetch("SELECT numip, port FROM sunservers WHERE alias='тест123';")
        assert answer == right_answer

    @mark.asyncio
    async def test_get_pings(self, database):
        """Проверяет функцию get_pings"""
        await database.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await database.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await database.make_tables()
        await database.add_ping('127.0.0.23', 25565, 1)
        await database.add_ping('127.0.0.23', 25565, 2)
        await database.add_ping('127.0.0.23', 25565, 3)
        answer = await database.get_pings('127.0.0.23', 25565)
        right_answer = await database.pool.fetch("SELECT * FROM sunpings WHERE ip='127.0.0.23' AND port=25565;")
        assert answer == right_answer

    @mark.asyncio
    async def test_get_pings_len(self, database):
        """Проверяет функцию get_pings_len"""
        await database.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await database.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await database.make_tables()
        await database.add_ping('127.0.0.24', 25565, 1)
        await database.add_ping('127.0.0.24', 25565, 2)
        await database.add_ping('127.0.0.24', 25565, 3)
        answer = await database.get_pings('127.0.0.24', 25565)
        assert len(answer) == 3

    class TestAnotherFunctions:
        """Класс для тестов других функций"""

    @mark.asyncio
    async def test_make_tables(self, database):
        """Проверяет функцию make_tables"""
        await database.make_tables()
        await database.pool.execute("SELECT * FROM sunpings;")
        await database.pool.execute("SELECT * FROM sunservers;")

    @mark.asyncio
    async def test_drop_table_sunpings(self, database):
        """Проверяет функцию drop_tables на таблице sunpings"""
        await database.make_tables()
        await database.add_ping('127.0.0.25', 25565, 333)
        await database.drop_tables()
        sunpings = await database.pool.fetch("SELECT * FROM sunpings;")
        assert len(sunpings) == 0

    @mark.asyncio
    async def test_drop_table_sunservers(self, database):
        """Проверяет функцию drop_tables на таблице sunservers"""
        await database.make_tables()
        await database.add_server('127.0.0.26', 0, 25565)
        await database.drop_tables()
        sunservers = await database.pool.fetch("SELECT * FROM sunservers;")
        assert len(sunservers) == 0
