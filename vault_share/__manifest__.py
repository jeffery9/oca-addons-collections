# © 2021-2024 Florian Kantelberg - initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Vault - Share",
    "summary": "Implementation of a mechanism to share secrets",
    "license": "AGPL-3",
    "version": "16.0.1.0.0",
    "website": "https://github.com/OCA/server-auth",
    "application": False,
    "author": "initOS GmbH, Odoo Community Association (OCA)",
    "category": "Vault",
    "depends": ["vault"],
    "data": [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/menuitems.xml",
        "views/res_config_settings_views.xml",
        "views/templates.xml",
        "views/vault_share_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "vault_share/static/src/common/**/*.js",
            "vault_share/static/src/backend/**/*.js",
            "vault_share/static/src/backend/**/*.scss",
            "vault_share/static/src/backend/**/*.xml",
        ],
        "vault_share.assets_frontend": [
            "vault/static/src/common/*.js",
            "vault_share/static/src/frontend/*.js",
        ],
    },
}
