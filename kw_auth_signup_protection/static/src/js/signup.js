odoo.define('kw_auth_signup_protection.signup', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

var SignUpForm = publicWidget.registry.SignUpForm;
if (!SignUpForm) {
    return;
}

SignUpForm.include({
    start: function () {
        var result = this._super.apply(this, arguments);
        this._kwInitRecaptcha();
        return result;
    },

    _kwInitRecaptcha: function () {
        var session = this.getSession();
        if (session && session.recaptcha_public_key) {
            var ReCaptcha = odoo.__DEBUG__.services['google_recaptcha.ReCaptchaV3'];
            if (ReCaptcha) {
                this._kwRecaptcha = new ReCaptcha();
                this._kwRecaptcha.loadLibs();
            }
        }
    },

    _onSubmit: function (ev) {
        if (this._kwRecaptcha) {
            ev.preventDefault();
            var self = this;
            this._kwRecaptcha.getToken('signup').then(function (resp) {
                if (resp.token) {
                    self.$('#recaptcha_token_response').val(resp.token);
                    self.$el[0].submit();
                } else if (resp.error) {
                    self.displayNotification({
                        type: 'danger',
                        title: resp.error,
                        sticky: true,
                    });
                }
            });
            return;
        }
        this._super.apply(this, arguments);
    },
});

});
