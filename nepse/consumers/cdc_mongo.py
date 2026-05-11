import datetime
import json

from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from django.apps import apps
from django.conf import settings
from django.db.models import DateTimeField

from mongoengine import connect

from nepse.models import Sector
from nepse.mongo_models import (
    SectorDoc, ShareGroupDoc, InstrumentTypeDoc,
    SecurityDoc, CompanyDoc, SecurityLogDoc,
)

connect(host=settings.MONGO_URL, alias='nepsedb')

SYNC_SETTINGS = {
    'nepse_sector': {
        'dj_model': 'nepse.sector',
        'mongo_model': SectorDoc,
    },
    'nepse_sharegroup': {
        'dj_model': 'nepse.sharegroup',
        'mongo_model': ShareGroupDoc,
    },
    'nepse_instrumenttype': {
        'dj_model': 'nepse.instrumenttype',
        'mongo_model': InstrumentTypeDoc,
    },
    'nepse_security': {
        'dj_model': 'nepse.security',
        'mongo_model': SecurityDoc,
    },
    'nepse_company': {
        'dj_model': 'nepse.company',
        'mongo_model': CompanyDoc,
    },
    'nepse_securitylog': {
        'dj_model': 'nepse.securitylog',
        'mongo_model': SecurityLogDoc,
    },
}


class MongoSync:
    def __init__(self, changes: dict):
        self.changes = changes
        self.table_alias = self.changes.get('source', {}).get('table')
        self.settings = SYNC_SETTINGS.get(self.table_alias)

        self.dj_model = apps.get_model(self.settings.get('dj_model'))
        self.mongo_model = self.settings.get('mongo_model')

        self.field_wise_handlers = {
            DateTimeField.__name__: self.handle_datetime_field
        }

        self.sanitize_changes()

    @property
    def op(self):
        return self.changes.get('op')

    @property
    def before(self):
        return self.changes.get('before', {})

    @property
    def after(self):
        return self.changes.get('after', {})

    @property
    def pk(self):
        return (
            (self.changes.get('before') or {}).get('id') or
            (self.changes.get('after') or {}).get('id')
        )

    def get_field_handler(self, field_name: str):
        for field in self.dj_model._meta.get_fields():
            if field.name == field_name:
                field_type = field.__class__.__name__
                return self.field_wise_handlers.get(field_type)

        return None

    @staticmethod
    def handle_datetime_field(raw_val: str):
        return (
            datetime.datetime
            .strptime(raw_val, "%Y-%m-%dT%H:%M:%S.%fZ")
            .replace(tzinfo=datetime.timezone.utc)
        )

    def sanitize_changes(self):
        for snapshot in ['before', 'after']:
            snapshot_data = self.changes.get(snapshot)
            if snapshot_data is not None:
                for field, val in snapshot_data.items():
                    field_handler = self.get_field_handler(field)
                    if field_handler is not None:
                        snapshot_data[field] = field_handler(val)

    def sync(self):
        print(f'#### DJ Model: {self.dj_model.__name__} - {self.pk}')
        print('#### Changes:', self.changes)
        try:
            if self.op == 'c':
                print('## Inserting ##')
                doc = self._insert()
                print('###############')
            elif self.op == 'u':
                print('## Updating ##')
                doc = self._update()
                print('###############')
            elif self.op == 'd':
                print('## Deleting ##')
                doc = self._delete()
                print('###############')
            else:
                doc = None

        except Exception as e:
            print()
            print(e)
            return None

        return doc

    def _insert(self):
        doc = self.mongo_model(**self.after)
        doc.save()
        return doc

    def _update(self):
        doc = self.mongo_model.objects(id=self.pk).first()

        if doc is None:
            return self._insert()

        for field, value in self.after.items():
            setattr(doc, field, value)

        doc.save()
        return doc

    def _delete(self):
        doc = self.mongo_model(id=self.pk)
        doc.delete()
        return None


class DBZConsumer:
    def __init__(self):
        # Set your schema registry URL
        self.schema_registry_conf = {'url': 'http://schemaregistry:8081'}
        self.schema_registry_client = SchemaRegistryClient(self.schema_registry_conf)

        # Avro deserializer: returns raw dict
        self.avro_deserializer = AvroDeserializer(
            self.schema_registry_client,
            from_dict=lambda d, ctx: d
        )

        # Kafka Consumer config
        self.consumer_conf = {
            'bootstrap.servers': 'broker:29092',  # port exposed by broker service
            'group.id': 'nepse-consumer',
            'auto.offset.reset': 'earliest'
        }

        self.consumer = Consumer(self.consumer_conf)

        self.TOPIC = [
            'cdc.public.nepse_sector',
            'cdc.public.nepse_sharegroup',
            'cdc.public.nepse_instrumenttype',
            'cdc.public.nepse_company',
            'cdc.public.nepse_security',
            'cdc.public.nepse_securitylog',
        ]

        print('Subscribed to topics:')
        print('\n'.join(f' - {topic}' for topic in self.TOPIC))

        self.consumer.subscribe(self.TOPIC)

    def poll_messages(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if not msg:
                    continue
                if msg.error():
                    print(f"Error: {msg.error()}")
                    continue

                record = self.avro_deserializer(
                    msg.value(),
                    SerializationContext(msg.topic(), MessageField.VALUE)
                )

                mongo_sync = MongoSync(changes=record)
                mongo_sync.sync()

        except KeyboardInterrupt:
            print("Aborted.")
        finally:
            self.consumer.close()
