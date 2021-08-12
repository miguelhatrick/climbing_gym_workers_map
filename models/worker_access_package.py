# -*- coding: utf-8 -*-
import logging
import pdb
from datetime import datetime, timedelta, date, timezone
from typing import List

import odoo
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WorkerAccessPackage(models.Model):
    """Worker Access package"""
    _name = 'climbing_gym.worker_access_package'
    _description = 'Worker Access package'
    _inherit = ['mail.thread']

    status_selection = [('pending', "Pending"), ('active', "Active"), ('cancel', "Cancelled")]

    name = fields.Char('Name', compute='_generate_name')
    department_id = fields.Many2one('hr.department', string='Department', track_visibility=True)
    obs = fields.Text('Observations')
    access_package = fields.Many2one('climbing_gym.access_package', string='Linked access package', required=True)
    state = fields.Selection(status_selection, 'Status', default='pending', track_visibility=True)

    @api.multi
    def action_revive(self):
        for _map in self:
            _map.state = 'pending'

    @api.multi
    def action_active(self):
        for _map in self:
            _map.state = 'active'

    @api.multi
    def action_cancel(self):
        for _map in self:
            _map.state = 'cancel'

    def action_create_worker_access_package(self):
        self.create_worker_maps()

    @api.multi
    def update_status_cron(self):
        """Cron job to keep everything tidy"""
        arr = self.env['climbing_gym.worker_access_package'].search(
            [('state', '=', "active")])
        _today = datetime.now().date()

        for _map in arr:
            _map.calculate_remaining_credits()
            if _map.date_finish < _today or _map.remaining_credits <= 0:
                _map.action_completed()

    def _generate_name(self):
        # pdb.set_trace()
        for _map in self:
            _map.name = "WAP-%s" % (_map.id if _map.id else '')

    def cron_create_worker_maps(self):
        """Creates MAPs for workers on all departments / Used once a month"""

        _logger.info('Begin cron_create_worker_maps Cron Job ... ')

        # Get all packages / departments
        _wap_ids = self.sudo().env['climbing_gym.worker_access_package'].search([('state', 'in', ['active'])])

        # For each WAP package go through employees and grab contacts
        for _wap_id in _wap_ids:
            _wap_id.create_worker_maps()

    def create_worker_maps(self):
        _logger.info('Processing WAP %s department %s' % (self.name, self.department_id.display_name))
        _partner_ids = [i.user_id.partner_id for i in self.department_id.member_ids if i.active and i.user_id is not None and i.user_id.partner_id is not None]

        _logger.info('Found %d workers who will receive a new package, processing ... ' % (len(_partner_ids)))

        # for each partner id create one access package
        self.create_access_package(_partner_ids)

        _logger.info('Finished cron_create_worker_maps Cron Job ... ')
        _now = datetime.now()

    def create_access_package(self, partner_ids):
        for partner_id in partner_ids:

            sale_order_line = False
            pos_order_line = False
            product_id = False

            # Access package can have its own multiplier.
            _map_qty = self.access_package.package_qty

            for x in range(0, _map_qty):
                _logger.info('Creating MAP -> %d / %d' % (x + 1, _map_qty))

                _my_map = self.sudo().env['climbing_gym.member_access_package'].create({
                    'partner_id': partner_id.id,
                    'obs': "WORKER PACKAGE\r\n" + " Qty item %s/%s\r\n Created automatically after order confirmation" % (x + 1, _map_qty),
                    'access_credits': self.access_package.access_credits,
                    'remaining_credits': self.access_package.access_credits,
                    'days_duration': self.access_package.days_duration,
                    'locations': [(6, 0, self.access_package.locations.ids)],
                    'product': product_id,
                    'sale_order_line': sale_order_line,
                    'pos_order_line': pos_order_line,
                    'access_package': self.access_package.id,
                    'state': 'pending',
                })

                _logger.info('Created MAP %d' % (_my_map.id))

                _logger.info('Activating MAP %d' % (_my_map.id))
                _my_map.action_active()


