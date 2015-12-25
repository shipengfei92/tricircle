# Copyright 2015 Huawei Technologies Co., Ltd.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import migrate
import sqlalchemy as sql


def upgrade(migrate_engine):
    meta = sql.MetaData()
    meta.bind = migrate_engine

    # remove after change the site management to pod management
    cascaded_sites = sql.Table(
        'cascaded_sites', meta,
        sql.Column('site_id', sql.String(length=64), primary_key=True),
        sql.Column('site_name', sql.String(length=64), unique=True,
                   nullable=False),
        sql.Column('az_id', sql.String(length=64), nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8')
    cascaded_site_service_configuration = sql.Table(
        'cascaded_site_service_configuration', meta,
        sql.Column('service_id', sql.String(length=64), primary_key=True),
        sql.Column('site_id', sql.String(length=64), nullable=False),
        sql.Column('service_type', sql.String(length=64), nullable=False),
        sql.Column('service_url', sql.String(length=512), nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8')

    pod_map = sql.Table(
        'pod_map', meta,
        sql.Column('id', sql.String(36), primary_key=True),
        sql.Column('az_name', sql.String(length=255), nullable=True),
        sql.Column('dc_name', sql.String(length=255), nullable=True),
        sql.Column('pod_name', sql.String(length=255), nullable=False),
        sql.Column('pod_az_name', sql.String(length=255),
                   nullable=True),
        sql.Column('created_at', sql.DateTime),
        sql.Column('updated_at', sql.DateTime),
        migrate.UniqueConstraint(
            'az_name', 'pod_name',
            name='pod_map0az_name0pod_name'),
        mysql_engine='InnoDB',
        mysql_charset='utf8')

    pod_binding = sql.Table(
        'pod_binding', meta,
        sql.Column('id', sql.String(36), primary_key=True),
        sql.Column('tenant_id', sql.String(length=255), nullable=False),
        sql.Column('az_pod_map_id', sql.String(length=255), nullable=False),
        sql.Column('created_at', sql.DateTime),
        sql.Column('updated_at', sql.DateTime),
        migrate.UniqueConstraint(
            'tenant_id', 'az_pod_map_id',
            name='pod_binding0tenant_id0az_pod_map_id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8')

    tables = [cascaded_sites, cascaded_site_service_configuration,
              pod_map, pod_binding]
    for table in tables:
        table.create()

    # remove after change the site management to pod management
    fkey = {'columns': [cascaded_site_service_configuration.c.site_id],
            'references': [cascaded_sites.c.site_id]}
    migrate.ForeignKeyConstraint(columns=fkey['columns'],
                                 refcolumns=fkey['references'],
                                 name=fkey.get('name')).create()

    fkey = {'columns': [pod_binding.c.az_pod_map_id],
            'references': [pod_map.c.id]}
    migrate.ForeignKeyConstraint(columns=fkey['columns'],
                                 refcolumns=fkey['references'],
                                 name=fkey.get('name')).create()


def downgrade(migrate_engine):
    raise NotImplementedError('can not downgrade from init repo.')
