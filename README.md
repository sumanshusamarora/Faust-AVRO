# Faust-AVRO
The repo consists code to automatically generate avro schema from Faust records. On top of it, some new derived classes of basic data types have been created to utilize null functonality of avro schema.

The repo also contains utility to convert faust record to avro json and byte message and vice versa.

## Requirements
- python==3.6
- faust==1.10.4
- avro-json-serializer==1.0.1
- avro-python3==1.8.2
- fastavro==0.23.4
- typing-extensions==3.7.4.2
- datetime

## Data Types
str - For string, should not be None

strNull - For string, can be None (will be represented as ["null", "str"] in avro schema)

int - For integeres, should not be None

intNull - For Int, can be None (will be represented as ["null", "int"] in avro schema)

float - For float values, should not be None

floatNull - For float, can be None (will be represented as ["null", "double"] in avro schema)

datetime.datetime - For datetime values, should not be None (will be represented as string in avro schema)

datetimeNull - For datetime, can be None (will be represented as ["null", "str"] in avro schema)

datetime.date - For date values, should not be None (will be represnted as string in avro schema)

dateNull - For date values, can be None (will be represented as ["null", "str"] in avro schema)

typing.List - For homogeneous lists of single type of objects. List should not be empty

typingListNull - For homogeneous lists of single type of objects. List can be empty


## Examples

```
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
    Attachments: typingListNull.List(Attachment)


file1 = Attachment(Name="foo.bar", Location="fooBar/fooBar/fooBar/fooBar")
file2 = Attachment(Name="foobar.foo", Location=None)

employee1 = Employee(name='Foo', email="foo.bar@foobar.com", designation=None, salary=150320.2, numberOfReportees=3, managerName="Bar Foo")
employee2 = Employee(name='FooBar', email="foobar.foo@foobar.com", designation="SM", salary=None, numberOfReportees=1, managerName=None)
employee3 = Employee(name='Bar',email="bar.foo@foobar.com", designation=None, salary=None, numberOfReportees=None, managerName=None)
employee4 = Employee(name='BarFoo', email="barfoo.foo@foobar.com", designation=None, salary=1254002.0, numberOfReportees=None, managerName='Foo')

email1 = EmailRecord(received=datetime.datetime.now(), fromAddress=employee1, toAddress=[employee3, employee4], ccAddress=[employee2], subject='Foo', body='Bar', Attachments=[])
email2 = EmailRecord(received=datetime.datetime.now(), fromAddress=employee3, toAddress=[employee1], ccAddress=[], subject='Foo', body='Bar', Attachments=[file1])
email3 = EmailRecord(received=datetime.datetime.now(), fromAddress=employee4, toAddress=[employee2, employee1, employee3], ccAddress=[employee2, employee1, employee3], subject='Foo', body='Bar', Attachments=[file1, file2])
```

Now we can simply call avro_equivalent() method on a faust record instance wich returns the avro schema and also the same faust record. Please note that original record gets changed after calling this method so it is important to replace the original faust ecord with the returnd faust record.

```
avro_schema1, email1 = email1.avro_equivalent()
avro_schema2, email2 = email2.avro_equivalent()
```
Generatedavro schema
```
{'name': 'EmailRecord', 'type': 'record', 'namespace': 'com.avro', 'fields': [{'name': 'received', 'type': 'string'}, {'name': 'fromAddress', 'type': {'name': 'EmployeeData', 'type': 'record', 'namespace': 'com.avro', 'fields': [{'name': 'name', 'type': 'string'}, {'name': 'email', 'type': 'string'}, {'name': 'designation', 'type': ['string', 'null']}, {'name': 'salary', 'type': ['null', 'double']}, {'name': 'numberOfReportees', 'type': ['string', 'null']}, {'name': 'managerName', 'type': ['string', 'null']}]}}, {'name': 'toAddress', 'type': ['null', {'type': 'array', 'items': {'name': 'EmployeeData', 'type': 'record', 'namespace': 'com.avro', 'fields': [{'name': 'name', 'type': 'string'}, {'name': 'email', 'type': 'string'}, {'name': 'designation', 'type': ['string', 'null']}, {'name': 'salary', 'type': ['null', 'double']}, {'name': 'numberOfReportees', 'type': ['string', 'null']}, {'name': 'managerName', 'type': ['string', 'null']}]}}]}, {'name': 'ccAddress', 'type': ['null', {'type': 'array', 'items': {'name': 'EmployeeData', 'type': 'record', 'namespace': 'com.avro', 'fields': [{'name': 'name', 'type': 'string'}, {'name': 'email', 'type': 'string'}, {'name': 'designation', 'type': ['string', 'null']}, {'name': 'salary', 'type': ['null', 'double']}, {'name': 'numberOfReportees', 'type': ['string', 'null']}, {'name': 'managerName', 'type': ['string', 'null']}]}}]}, {'name': 'subject', 'type': ['string', 'null']}, {'name': 'body', 'type': ['string', 'null']}, {'name': 'Attachments', 'type': ['null', {'type': 'array', 'items': {'name': 'AttachmentData', 'type': 'record', 'namespace': 'com.avro', 'fields': [{'name': 'Name', 'type': 'string'}, {'name': 'Location', 'type': ['string', 'null']}]}}]}]}
```

Irrespective of the values provided into the record instance the avro schema should be same so -
```
avro_schema1 == avro_schema2
True
```

To use the same schema and then generate byte or json avro message, below code can be refernced
```
avro_schema, email = email1.avro_equivalent()
faust2avro = faustToAvro(base_object=email, avro_schema=avro_schema)
result_dict = faust2avro.iterate()
bytes_serialized = faust2avro.serialize_to_bytes(result_dict)
json_serialized = faust2avro.serialize_to_json(result_dict)
```
For other details on how to use, please look at the examples.py file.

## Issues
This is just a basic implementation that has been done to solve some problems i was facing during my project. I do not plan to improve this further but if you find any issues, please free to raise issues on this guthub repo and i will try to fix them.
    
 


