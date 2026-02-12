import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class KwAutocompleteMixin(models.AbstractModel):
    _name = 'kw.autocomplete.mixin'
    _description = 'Autocomplete Helper Mixin'

    @api.model
    def kw_autocomplete_search(self, query, field_name, domain=None,
                               limit=10, dep_values=None, display_fields=None,
                               label_template=None, value_field=None):
        """Generic autocomplete search for domain-based sources.

        Args:
            query: Search string
            field_name: Field to search in
            domain: Additional domain filters
            limit: Maximum results
            dep_values: Dict of dependent field values
            display_fields: List of fields to return
            label_template: Template for label formatting
            value_field: Field to use as value

        Returns:
            List of dicts with 'label', 'value', 'data' keys
        """
        search_domain = list(domain) if domain else []
        if query:
            search_domain.append((field_name, 'ilike', query))

        if dep_values:
            for field, value in dep_values.items():
                if value:
                    if isinstance(value, (list, tuple)) and len(value) >= 1:
                        value = value[0]
                    search_domain.append((field, '=', value))

        if display_fields:
            fields_to_read = list(display_fields)
        else:
            fields_to_read = [field_name]
        if 'id' not in fields_to_read:
            fields_to_read.append('id')

        records = self.search_read(
            search_domain,
            fields_to_read,
            limit=limit
        )

        value_fld = value_field or field_name
        result = []
        for r in records:
            if label_template:
                label = label_template
                for fld in fields_to_read:
                    fld_val = str(r.get(fld, '') or '')
                    label = label.replace('{%s}' % fld, fld_val)
            else:
                label = r.get(value_fld, '')

            result.append({
                'label': label,
                'value': r.get(value_fld, ''),
                'data': r,
            })

        return result

    @api.model
    def kw_autocomplete_proxy_rest(self, query, config, dep_values=None):
        """Proxy method for REST API calls (security wrapper).

        Config should contain:
            - credential_model: Model name for credentials
            - credential_id: ID of credential record (optional)
            - credential_method: Method to get credential (optional)
            - endpoint: API endpoint path
            - query_param: Parameter name for query
            - method: HTTP method (GET/POST)
            - result_path: Dot-notation path to results in response
            - label_field: Field name for label
            - value_field: Field name for value

        Returns:
            List of dicts with 'label', 'value', 'data' keys
        """
        credential_model = config.get('credential_model')
        if not credential_model:
            _logger.warning('No credential_model in REST API config')
            return []

        Credential = self.env.get(credential_model)
        if Credential is None:
            _logger.warning('Model %s not found', credential_model)
            return []

        credential_id = config.get('credential_id')
        credential_method = config.get('credential_method')

        if credential_id:
            credential = Credential.browse(credential_id)
        elif credential_method and hasattr(Credential, credential_method):
            credential = getattr(Credential, credential_method)()
        else:
            credential = Credential.search([], limit=1)

        if not credential or not credential.exists():
            _logger.warning('No credential found for REST API')
            return []

        params = {config.get('query_param', 'q'): query}
        if dep_values:
            params.update(dep_values)

        method = config.get('method', 'GET')
        endpoint = config.get('endpoint', '')

        try:
            if hasattr(credential, 'api_request'):
                if method == 'GET':
                    response = credential.api_request(
                        method='GET',
                        url=endpoint,
                        params=params,
                        silent=True
                    )
                else:
                    response = credential.api_request(
                        method='POST',
                        url=endpoint,
                        json=params,
                        silent=True
                    )
            else:
                _logger.warning('Credential model has no api_request method')
                return []
        except Exception as e:
            _logger.error('REST API error: %s', str(e))
            return []

        if not response:
            return []

        results = response
        result_path = config.get('result_path', '')
        if result_path:
            for key in result_path.split('.'):
                if isinstance(results, dict):
                    results = results.get(key, [])
                else:
                    break

        if not isinstance(results, list):
            results = [results] if results else []

        label_field = config.get('label_field', 'name')
        value_field = config.get('value_field', 'name')

        return [{
            'label': r.get(label_field, '') if isinstance(r, dict) else str(r),
            'value': r.get(value_field, '') if isinstance(r, dict) else str(r),
            'data': r,
        } for r in results]
