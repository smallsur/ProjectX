from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy import text # TextClause类
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from instances import Reserve_Point


# CursorResult类
result = select(Reserve_Point).where(Reserve_Point.id == 123)

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)


with engine.begin() as conn:#自动提交
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}]
    )


with engine.connect() as conn:
    conn.execute(
        text("SELECT x, y FROM some_table WHERE y > :y"),
        {"y": 2}
    )#单个参数

    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 11, "y": 12}, {"x": 13, "y": 14}]
    )#多个参数, cursor调用cursor.excutemany()

    result = conn.execute(text("SELECT x, y FROM some_table"))#返回类似 namedtuple 结构
    for row in result:
        print(f"x: {row.x}  y: {row.y}")

    conn.excute(text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=6))
    #绑定参数


    conn.commit()#


#session构造
with Session(engine) as session:
    result = session.execute(text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=6))
    for row in result:
       print(f"x: {row.x}  y: {row.y}")


########################################################################
metadata_obj = MetaData()
from sqlalchemy import Table, Column, Integer, String
user_table = Table(
    "user_account",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String(30)),
    Column('fullname', String)
)
user_table.c.name
user_table.c.keys()

from sqlalchemy import ForeignKey
address_table = Table(
    "address",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('user_account.id'), nullable=False),
    Column('email_address', String, nullable=False)
)
metadata_obj.create_all(engine)#创建所有表
metadata_obj.drop_all(engine)#删除所有表

################################################################################

from sqlalchemy.orm import registry
mapper_registry = registry() 
mapper_registry.metadata # mapper_registry包含Metadata()
Base = mapper_registry.generate_base()#


from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = 'user_account'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)

    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
       return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user_account.id'))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"

mapper_registry.metadata.create_all(engine)
Base.metadata.create_all(engine)

#反射，从数据库读取数据，自动映射需要的表，返回对象
some_table = Table("some_table", metadata_obj, autoload_with=engine)


#################################################################################

from sqlalchemy import insert
stmt = insert(user_table).values(name='spongebob', fullname="Spongebob Squarepants")

#生成sql语句
compiled = stmt.compile()

#绑定的参数
compiled.params

with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.inserted_primary_key)#插入结果的主键，元组类型

    result = conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patrick", "fullname": "Patrick Star"}
        ]
    )#多行自动构建

    conn.commit()
    
#高级炼金术
from sqlalchemy import select, bindparam
scalar_subq = (
    select(user_table.c.id).
    where(user_table.c.name==bindparam('username')).
    scalar_subquery()
)
with engine.connect() as conn:
    result = conn.execute(
        insert(address_table).values(user_id=scalar_subq),
        [
            {"username": 'spongebob', "email_address": "spongebob@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@squirrelpower.org"},
        ]
    )
    conn.commit()
# BEGIN (implicit)
# INSERT INTO address (user_id, email_address) VALUES ((SELECT user_account.id
# FROM user_account
# WHERE user_account.name = ?), ?)
# [...] (('spongebob', 'spongebob@sqlalchemy.org'), ('sandy', 'sandy@sqlalchemy.org'),
# ('sandy', 'sandy@squirrelpower.org'))
# COMMIT

###########################################################################

#
stmt = select(user_table).where(user_table.c.name == 'spongebob')

select(user_table.c.name, user_table.c.fullname)


#返回第一行，
row = session.execute(select(User)).first()

select(User.name, User.fullname)#不带标签查询


#连接查询
session.execute(
    select(User.name, Address).
    where(User.id==Address.user_id).
    order_by(Address.id)
).all()


#带标签查询
from sqlalchemy import func, cast
stmt = (
    select(
        ("Username: " + user_table.c.name).label("username"),
    ).order_by(user_table.c.name)
)
with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(f"{row.username}")
# SELECT ? || user_account.name AS username
# FROM user_account ORDER BY user_account.name
# [...] ('Username: ',)


#插入常量表达式
from sqlalchemy import literal_column
stmt = (
    select(
        text("'some phrase'"), user_table.c.name
    ).order_by(user_table.c.name)
)
stmt = (
    select(
        literal_column("'some phrase'").label("p"), user_table.c.name
    ).order_by(user_table.c.name)
)


#where语句
#连续嵌套，相当于and
print(
    select(address_table.c.email_address).
    where(user_table.c.name == 'squidward').
    where(address_table.c.user_id == user_table.c.id)
)
#一个where，多个参数
print(
    select(address_table.c.email_address).
    where(
         user_table.c.name == 'squidward',
         address_table.c.user_id == user_table.c.id
    )
)
from sqlalchemy import and_, or_
#逻辑函数
print(
    select(Address.email_address).
    where(
        and_(
            or_(User.name == 'squidward', User.name == 'sandy'),
            Address.user_id == User.id
        )
    )
)

#filter_by
print(
    select(User).filter_by(name='spongebob', fullname='Spongebob Squarepants')
)

#join
print(
    select(user_table.c.name, address_table.c.email_address).
    join_from(user_table, address_table)
)
print(
    select(user_table.c.name, address_table.c.email_address).
    join(address_table)
)
print(
    select(address_table.c.email_address).
    select_from(user_table).join(address_table)
)



#func
from sqlalchemy import func
print (
    select(func.count('*')).select_from(user_table)
)
# SELECT count(:count_2) AS count_1
# FROM user_account




#显示指定连接属性
print(
    select(address_table.c.email_address).
    select_from(user_table).
    join(address_table, user_table.c.id == address_table.c.user_id)
)

#左外部链接和完全链接
print(
    select(user_table).join(address_table, isouter=True)
)
print(
    select(user_table).join(address_table, full=True)
)


# 排序 orderby
print(select(user_table).order_by(user_table.c.name))


#聚合函数 
from sqlalchemy import func
count_fn = func.count(user_table.c.id)

#
with engine.connect() as conn:
    result = conn.execute(
        select(User.name, func.count(Address.id).label("count")).
        join(Address).
        group_by(User.name).
        having(func.count(Address.id) > 1)
    )
    print(result.all())

from sqlalchemy import func, desc
stmt = select(
        Address.user_id,
        func.count(Address.id).label('num_addresses')).\
        group_by("user_id").order_by("user_id", desc("num_addresses"))
# SELECT address.user_id, count(address.id) AS num_addresses
# FROM address GROUP BY address.user_id ORDER BY address.user_id, num_addresses DESC

#子查询
#subquery
subq = select(
    func.count(address_table.c.id).label("count"),
    address_table.c.user_id
).group_by(address_table.c.user_id).subquery()

stmt = select(
   user_table.c.name,
   user_table.c.fullname,
   subq.c.count
).join_from(user_table, subq)
#cte
subq = select(
    func.count(address_table.c.id).label("count"),
    address_table.c.user_id
).group_by(address_table.c.user_id).cte()
stmt = select(
   user_table.c.name,
   user_table.c.fullname,
   subq.c.count
).join_from(user_table, subq)





session.add()
session.flush()
#添加元素，内存有映射
some_squidward = session.get(User, 4)
some_squidward
User(id=4, name='squidward', fullname='Squidward Tentacles')

#返回设置
result.scalar_one()


#dirty表示集合，修改存储，修改过的类会保存在里面
session.dirty

