import json
from extensions import db
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Float, JSON

"""
This class is used to create(or use existing table) a device_logs table in the database
"""
class DeviceEventLog2023(db.Model):
    __tablename__ = "device_logs"
    id = Column(Integer, autoincrement=True, primary_key=True)
    entity_id = Column(String)
    key = Column(db.Integer)
    ts = Column(BigInteger)
    bool_v = Column(Boolean)
    str_v = Column(String)
    long_v = Column(BigInteger)
    dbl_v = Column(Float(precision=53))
    json_v = Column(String)

    # Its purpose is to convert a database model instance into a plain Python dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "key": self.key,
            "ts": self.ts,
            "bool": self.bool_v,
            "str_v": self.str_v,
            "long_v": self.long_v,
            "dbl_v": self.dbl_v,
            "json_v": self.json_v,
        }

    def __repr__(self) -> str:
        return f"id {self.id} entity_id {self.entity_id} key {self.key} ts {self.ts} bool {self.bool} str_v {self.str_v} long_v {self.long_v} dbl_v{self.dbl_v} json_v {self.json_v} "




"""
This class is used to create(or use existing table) a device_logs_demo table in the database
"""
class DeviceEventLogfifty(db.Model):
    __tablename__ = "device_logs_50000"
    id = Column(Integer, autoincrement=True, primary_key=True)
    entity_id = Column(String)
    key = Column(db.Integer)
    ts = Column(BigInteger)
    bool_v = Column(Boolean)
    str_v = Column(String)
    long_v = Column(BigInteger)
    dbl_v = Column(Float(precision=53))
    json_v = Column(String)

    # Its purpose is to convert a database model instance into a plain Python dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "key": self.key,
            "ts": self.ts,
            "bool": self.bool_v,
            "str_v": self.str_v,
            "long_v": self.long_v,
            "dbl_v": self.dbl_v,
            "json_v": self.json_v,
        }

    def __repr__(self) -> str:
        return f"id {self.id} entity_id {self.entity_id} key {self.key} ts {self.ts} bool {self.bool} str_v {self.str_v} long_v {self.long_v} dbl_v{self.dbl_v} json_v {self.json_v} "






"""
This class is used to create(or use existing table) a compressed_device_logs table in the database
"""
class CompressedDeviceEventLog(db.Model):
    __tablename__ = "compressed_device_logs"
    id = Column(Integer, autoincrement=True, primary_key=True)
    entity_id = Column(String)
    key = Column(db.Integer)
    ts = Column(BigInteger)
    bool_v = Column(Boolean)
    str_v = Column(String)
    long_v = Column(BigInteger)
    dbl_v = Column(Float(precision=53))
    json_v = Column(String)

    # Its purpose is to convert a database model instance into a plain Python dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "key": self.key,
            "ts": self.ts,
            "bool": self.bool,
            "str_v": self.str_v,
            "long_v": self.long_v,
            "dbl_v": self.dbl_v,
            "json_v": self.json_v,
        }

    def __repr__(self) -> str:
        return f"id {self.id} entity_id {self.entity_id} key {self.key} ts {self.ts} bool {self.bool} str_v {self.str_v} long_v {self.long_v} dbl_v{self.dbl_v} json_v {self.json_v} "





"""
This class is used to create(or use existing table) a device_logs_demo table in the database
"""
class DeviceEventLogthousand(db.Model):
    __tablename__ = "device_logs_1000"
    id = Column(Integer, autoincrement=True, primary_key=True)
    entity_id = Column(String)
    key = Column(db.Integer)
    ts = Column(BigInteger)
    bool_v = Column(Boolean)
    str_v = Column(String)
    long_v = Column(BigInteger)
    dbl_v = Column(Float(precision=53))
    json_v = Column(String)

    # Its purpose is to convert a database model instance into a plain Python dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "key": self.key,
            "ts": self.ts,
            "bool": self.bool_v,
            "str_v": self.str_v,
            "long_v": self.long_v,
            "dbl_v": self.dbl_v,
            "json_v": self.json_v,
        }

    def __repr__(self) -> str:
        return f"id {self.id} entity_id {self.entity_id} key {self.key} ts {self.ts} bool {self.bool} str_v {self.str_v} long_v {self.long_v} dbl_v{self.dbl_v} json_v {self.json_v} "






"""
This class is used to create(or use existing table) a compressed_device_logs table in the database
"""
class CompressedDeviceEventLog2(db.Model):
    __tablename__ = "compressed_device_logs_ts_kv_2024_06"
    id = Column(Integer, autoincrement=True, primary_key=True)
    entity_id = Column(String)
    key = Column(db.Integer)
    ts = Column(BigInteger)
    bool_v = Column(String)
    str_v = Column(String)
    long_v = Column(BigInteger)
    dbl_v = Column(Float(precision=53))
    json_v = Column(String)

    # Its purpose is to convert a database model instance into a plain Python dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "key": self.key,
            "ts": self.ts,
            "bool_v": self.bool_v,
            "str_v": self.str_v,
            "long_v": self.long_v,
            "dbl_v": self.dbl_v,
            "json_v": self.json_v,
        }

    def __repr__(self) -> str:
        return f"id {self.id} entity_id {self.entity_id} key {self.key} ts {self.ts} bool {self.bool} str_v {self.str_v} long_v {self.long_v} dbl_v{self.dbl_v} json_v {self.json_v} "




"""
This class is used to create(or use existing table) a device_logs table in the database
"""
class DeviceEventLog(db.Model):
    __tablename__ = "device_logs_ts_kv_2024_06"
    id = Column(Integer, autoincrement=True, primary_key=True)
    entity_id = Column(String)
    key = Column(db.Integer)
    ts = Column(BigInteger)
    bool_v = Column(String)
    str_v = Column(String)
    long_v = Column(BigInteger)
    dbl_v = Column(Float(precision=53))
    json_v = Column(String)

    # Its purpose is to convert a database model instance into a plain Python dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "key": self.key,
            "ts": self.ts,
            "bool": self.bool_v,
            "str_v": self.str_v,
            "long_v": self.long_v,
            "dbl_v": self.dbl_v,
            "json_v": self.json_v,
        }

    def __repr__(self) -> str:
        return f"id {self.id} entity_id {self.entity_id} key {self.key} ts {self.ts} bool {self.bool} str_v {self.str_v} long_v {self.long_v} dbl_v{self.dbl_v} json_v {self.json_v} "

