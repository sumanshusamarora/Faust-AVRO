import kafka
import json
import faust
import avro
import io
import avro.io
import avro.schema
from datetime import datetime, date
from avro.schema import SchemaFromJSONData as make_avsc_object
from avro_json_serializer import AvroJsonSerializer, AvroJsonDeserializer

class faustToAvro():
    def __init__(self, base_object=None, base_class=faust.Record, avro_schema=None):
        self.base_class = base_class
        self.base_object = base_object
        self.result_dict = dict()
        self.avro_schema = avro_schema
        """
        if self.base_object.__class__.__base__ != self.base_class:
            raise ValueError("Not a Faust record")
            """

    def convert_to_dict(self, obj):
        return self.obj.asdict()

    def _is_base_class_object(self, obj):
        if obj.__class__.__base__ == self.base_class:
            return True
        return None

    def _is_list(self, obj):
        if isinstance(obj, list):
            return True
        return None

    def _is_datetime(self, obj):
        if isinstance(obj, date) or isinstance(obj, datetime):
            return True
        return None

    def iterate(self, record_obj=None):
        result_dict = dict()
        if not record_obj:
            record_dict = self.base_object.asdict()
            obj_annotation = self.base_object.__annotations__
        else:
            record_dict = record_obj.asdict()
            obj_annotation = record_obj.__annotations__

        for ind, item in enumerate(record_dict.items()):
            key = item[0]
            val = item[1]

            if self._is_list(val):
                logger.info(f"Found list within Record")
                internal_list = []
                for el in val:
                    if self._is_base_class_object(el):
                        logger.info(f"Found base class object within list")
                        internal_list.append(self.iterate(record_obj=el))
                    elif self._is_datetime(el):
                        logger.info(f"Found datetime/date class object within list")
                        internal_list.append(str(el))
                    else:
                        internal_list.append(el)
                result_dict[key] = internal_list

            elif self._is_base_class_object(val):
                logger.info(f"{str(val)} is a base class object")
                result_dict[key] = self.iterate(record_obj=val)

            elif self._is_datetime(val):
                logger.info(f"{str(val)} is a datetime/date object")
                result_dict[key] = str(val)


            else:
                result_dict[key] = val

        return result_dict

    def serialize_to_json(self, result_dict):
        avro_schema = make_avsc_object(self.avro_schema, avro.schema.Names())
        serializer = AvroJsonSerializer(avro_schema)
        return serializer.to_json(result_dict)

    def serialize_to_bytes(self, result_dict):
        if not isinstance(self.avro_schema, bytes):
            avro_schema = json.dumps(self.avro_schema).encode('utf-8')
        else:
            avro_schema = self.avro_schema
        schema = avro.schema.Parse(avro_schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer = avro.io.DatumWriter(schema)
        writer.write(result_dict, encoder)
        raw_bytes = bytes_writer.getvalue()
        return raw_bytes

    def byte_to_faust(self, record):
        if not self.base_object.__class__.__base__ != self.base_class:
            logger.error("Not a valid faust record")
        if not self.avro_schema:
            logger.error("Provide a valid AVRO schema")

        if isinstance(self.avro_schema, list):
            self.avro_schema = json.dumps(self.avro_schema)

        schema = avro.schema.Parse(self.avro_schema)
        bytes_reader = io.BytesIO(record)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(schema)
        datum = reader.read(decoder)
        return self.base_object(**datum)

    def save_schema(self, name=None, dir=None):
        if not name:
            return None

        if not dir:
            dir = SCHEMA_DIR

        try:
            with open(os.path.join(dir, name+'.avsc'), 'wb') as fp:
                fp.write(json.dumps(self.avro_schema).encode('utf-8'))

            return os.path.join(dir, name+'.avsc')
        except Exception as e:
            return str(e)

        return None

    def json_to_faust(self, record):
        return AvroJsonDeserializer(self.avro_schema).from_json(record)

