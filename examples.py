from faustAvro import intNull, floatNull, strNull, datetimeNull, dateNull, typingListNull, AvroFaust
from FaustToAvroJsonBytes import faustToAvro
import faust
import typing

class Attachment(faust.Record, AvroFaust):
    Name: str
    Location: strNull
    
class Employee(faust.Record, AvroFaust):
    name: str
    email: str
    designation: strNull
    salary: floatNull
    numberOfReportees: intNull
    managerName: strNull
    
class EmailRecord(faust.Record, AvroFaust):
    received: datetime.datetime
    fromAddress: Employee
    toAddress: typing.List[Employee]
    ccAddress: typingListNull.List(Employee)
    subject: strNull
    body: strNull
    fileAttachments: typingListNull.List(Attachment)


file1 = Attachment(Name="foo.bar", Location="fooBar/fooBar/fooBar/fooBar")
file2 = Attachment(Name="foobar.foo", Location=None)

employee1 = Employee(name='Foo', email="foo.bar@foobar.com", designation=None, salary=150320.2, numberOfReportees=3, managerName="Bar Foo")
employee2 = Employee(name='FooBar', email="foobar.foo@foobar.com", designation="SM", salary=None, numberOfReportees=1, managerName=None)
employee3 = Employee(name='Bar',email="bar.foo@foobar.com", designation=None, salary=None, numberOfReportees=None, managerName=None)
employee4 = Employee(name='BarFoo', email="barfoo.foo@foobar.com", designation=None, salary=1254002.0, numberOfReportees=None, managerName='Foo')

email1 = EmailRecord(received=datetime.datetime.now(), fromAddress=employee1, toAddress=[employee3, employee4], ccAddress=[employee2], subject='Foo', body='Bar', Attachment=[])
email2 = EmailRecord(received=datetime.datetime.now(), fromAddress=employee3, toAddress=[employee1], ccAddress=[], subject='Foo', body='Bar', Attachment=[file1])
email3 = EmailRecord(received=datetime.datetime.now(), fromAddress=employee4, toAddress=[employee2, employee1, employee3], ccAddress=[employee2, employee1, employee3], subject='Foo', body='Bar', Attachment=[file1, file2])

#Now we can simply call avro_equivalent() method on a faust record instance wich returns the avro schema and also the same faust record. Please note that original record gets changed after calling this method so it is important to replace the original faust ecord with the returnd faust record
avro_schema1, email1 = email1.avro_equivalent()
avro_schema2, email2 = email2.avro_equivalent()

#Regardless of values provided into the record instance the avro schema should be same so schema once generated can be shared with someone who is consuimg the message
avro_schema1 == avro_schema2
True

#To use the same schema and then generate byte or json avro message, below code can be refernced
avro_schema, email = email1.avro_equivalent()
faust2avro = faustToAvro(base_object=email, avro_schema=avro_schema)
result_dict = faust2avro.iterate()
bytes_serialized = faust2avro.serialize_to_bytes(result_dict)
json_serialized = faust2avro.serialize_to_json(result_dict)


#To read a avro message and convert to Faust record
with open(f'{PATH TO SCHEMA DIRECTORY}/email.avsc', 'rb') as schema_file:
    email_schema =  schema_file.read()
    
@app.agent(subscribe, sink=[publish])
async def fetch(records):
    async for record in records:
        avro2faust = faustToAvro(base_object=EmailRecord, avro_schema=email_schema) #EmailRecord is simply the name of the Faust record you expect the avro message to convert to 
        record = avro2faust.byte_to_faust(record=record)
