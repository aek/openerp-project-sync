# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 Coop. Trab. Moldeo Interactive Ltda.
# http://business.moldeo.coop
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import logging
from datetime import datetime
import xmlrpclib

_logger = logging.getLogger(__name__)

class RPCProxy(object):
        def __init__(self, uid, passwd,
                host,
                port,
                dbname,
                path='object'):
            self.rpc = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/%s' % (host, port, path), allow_none=True)
            self.user_id = uid
            self.passwd = passwd
            self.dbname = dbname

        def __call__(self, *request, **kwargs):
            return self.rpc.execute(self.dbname, self.user_id, self.passwd, *request, **kwargs)


class project_sync(osv.osv):
    _name = "project.sync"
    _columns = {
        'name': fields.char('Name', size=64, select=True, required=True),
        'remote_project': fields.char('Remote project', size=64, select=True),
        'remote_server': fields.char('Remote server', size=64, select=True),
        'remote_user_id': fields.many2one('res.users', 'Remote user'),
        'project_id': fields.many2one('project.project', 'Project'),
        'timestamp': fields.date('Last Sync date', readonly=True), #TODO: Must be datetime
    }

    def do_sync(self, cr, uid, ids, context=None):
        """
        """
        task_obj = self.pool.get('project.task')
        users_obj = self.pool.get('res.users')
        context = context or {}

        res = {}
        
        for ps in self.browse(cr, uid, ids,context=context):
            task_ids = task_obj.search(cr, uid, [
                    ("user_id","=",ps.remote_user_id.id)],
                    context=context
            )
            tasks = task_obj.browse(cr, uid, task_ids, context=context)
            uid, password, host, port, dbname = ps.remote_server.split(':')

            rpc = RPCProxy(uid, password, host=host, port=port, dbname=dbname)

            rpc('project.sync',
                    'sync_process',
                    len(tasks)) # task_dict)

            _logger.info(ps.name)

        self.write(cr, uid, ids, {
            'timestamp': datetime.now().strftime('%Y-%m-%d'),
        })

        return res

    def sync_process(self, cr, uid, *args):
            import pdb; pdb.set_trace()

project_sync()

