from enum import Enum


class UserEnum(Enum):
    ROOT = "超级管理员"
    SCHOOL = "校级"
    ACADEMY = "院级"
    STUDENT = "干部级"
