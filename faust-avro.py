import datetime
import faust
import typing
import pdb
import copy

class intNull(int):
    def __init__(self):
        super(intNull, self).__init__()

class floatNull(float):
    def __init__(self):
        super(floatNull, self).__init__()

class strNull(float):
    def __init__(self):
        super(strNull, self).__init__()

class dateNull(datetime.date):
    def __init__(self):
        super(dateNull, self).__init__()

class datetimeNull(datetime.datetime):
    def __init__(self):
        super(datetimeNull, self).__init__()

class typingListNull:
    @classmethod
    def List(self, obj):
        return_obj = typing.List[obj]
        return_obj.__derivedclass__ = 'typingListNull'
        return typing.List[obj]

class AvroFaust:
    def _is_faust_record(self, val):
        avro_name = None
        try:
            if val.__class__.__base__ == faust.Record:
                _self_name = str(val.__str__)
                avro_name = self.schema_domain+"."+_self_name[_self_name.find("'__str__' of"):_self_name.find("object at")].strip().split()[-1]
            elif val.__base__ == faust.Record:
                _self_name = str(val)[:-2].split('.')[-1]
                avro_name = self.schema_domain + "." + _self_name

            for schema in self.final_schema_list:
                if schema['name'] == _self_name:
                    schema['name'] = _self_name+"Data"
                    return schema

            return avro_name #Will arrive to this return when it cant find the schema in the list
        except:
            pass

    def _basic_schemas(self, key, val):
        if isinstance(val, (strNull, datetimeNull, dateNull)) or "class 'strNull'" in str(val) or "dateNull" in str(val) or "datetimeNull" in str(val):
            curr_item = {"name": key, "type": ["null", "string"]}
        elif isinstance(val, floatNull) or ("class" in str(val) and "floatNull'" in str(val)):
            curr_item = {"name": key, "type": ["null", "double"]}
        elif isinstance(val, intNull) or "class 'intNull'" in str(val):
            curr_item = {"name": key, "type": ["null", "int"]}
        elif isinstance(val, (str, datetime.datetime, datetime.date)) or "class 'str'" in str(val) or "datetime.datetime" in str(val) or "datetime.date" in str(val):
            curr_item = {"name": key, "type": "string"}
        elif isinstance(val, float) or ("class" in str(val) and "float'" in str(val)):
            curr_item = {"name": key, "type": "double"}
        elif isinstance(val, int) or "class 'int'" in str(val):
            curr_item = {"name": key, "type": "int"}
        else:
            curr_item = {"name": key, "type": ["string", "null"]}
        return curr_item

    def process_schema(self, class_schema_as_dict=None, add_default_null=False):
        return_items = []
        for item in class_schema_as_dict.items():
            key = item[0]
            val = item[1]
            if val.__base__ == faust.Record:
                curr_item = {"name": key, "type": self._is_faust_record(val)}

            elif val.__base__ == typing.List or isinstance(val, list):
                for el in val.__args__:
                    if el.__base__ == faust.Record:
                        try:
                            if val.__derivedclass__ == 'typingListNull':
                                curr_item = {"name": key, "type": ["null", {"type": "array", "items": self._is_faust_record(el)}]}
                            else:
                                raise Exception
                        except:
                            curr_item = {"name": key, "type": {"type": "array", "items": self._is_faust_record(el)}}
                    else:
                        curr_item = self._basic_schemas(key, el)
                    break
            else:
                curr_item =  self._basic_schemas(key, val)

            if curr_item:
                return_items.append(curr_item)
        return return_items



    def scan_schema(self, obj):
        avro_schema_dict = dict()
        class_schema_as_dict = obj.__annotations__
        if obj.__class__.__base__ == faust.Record:
            avro_schema_dict["name"] = str(obj.__class__)[:-2].split('.')[-1]
        elif obj.__base__ == faust.Record:
            avro_schema_dict["name"] = str(obj)[:-2].split('.')[-1]

        avro_schema_dict["type"] = 'record'
        avro_schema_dict["namespace"] = self.schema_domain
        avro_schema_dict["fields"] = self.process_schema(class_schema_as_dict)
        # Appending final faust thing
        return avro_schema_dict

    #Iterates through whole record and returns schema for all Records
    def _internal_avro_equivalent(self, scan_class=None):
        class_schema_as_dict = scan_class.__annotations__
        for item in class_schema_as_dict.items():
            default_null = False
            key = item[0]
            val = item[1]
            if isinstance(val, list) or val.__base__ == typing.List:
                for el in val.__args__:
                    if el.__base__ == faust.Record:
                        return_schema = self._internal_avro_equivalent(scan_class=el)
                        break
            elif val.__class__.__base__ == faust.Record or val.__base__ == faust.Record:
                return_schema = self._internal_avro_equivalent(scan_class=val)
        _schema = self.scan_schema(scan_class)
        self.final_schema_list.append(_schema)
        self.final_schema = _schema

    #First functions. Maintains all states
    def avro_equivalent(self, obj=None, schema_domain='com.anz.oacb.avro'):
        original_record = copy.deepcopy(self)
        self.schema_domain = schema_domain
        self.final_schema_list = []
        self.final_schema = None
        if obj:
            scan_class = obj
        else:
            scan_class = copy.deepcopy(self)
        if scan_class.__class__.__base__ == faust.Record:
            self._internal_avro_equivalent(scan_class=scan_class)
            return self.final_schema, original_record
        else:
            return None, original_record
            
