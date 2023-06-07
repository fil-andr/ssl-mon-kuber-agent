from subprocess import check_output,CalledProcessError
from datetime import datetime
import time
from dateutil import parser
from flask import request
from flask import Flask,render_template, request, flash
import os

vault_enabled = os.environ['VAULT_ENABLED']
proxy_injector_enabled = os.environ['PROXY_INJECTOR_ENABLED']
vault_svc_name = os.environ['VAULT_SVC_NAME']
proxy_inj_svc_name = os.environ['PROXY_INJ_SVC_NAME']
vault_ns = os.environ['VAULT_NS']
proxy_inj_ns = os.environ['PROXY_INJ_NS']


vault_string = f"echo QUIT | openssl s_client -servername {vault_svc_name}.{vault_ns}.svc.cluster.local -host {vault_svc_name}.{vault_ns}.svc.cluster.local -port 443 -showcerts |  sed -n '/BEGIN CERTIFICATE/,/END CERT/p' | openssl x509 -
text 2>/dev/null | sed -n 's/ *Not After : *//p'"
proxy_inj_string = f"echo QUIT | openssl s_client -servername {proxy_inj_svc_name}.{proxy_inj_ns}.svc.cluster.local -host {proxy_inj_svc_name}.{proxy_inj_ns}.svc.cluster.local -port 443 -showcerts |  sed -n '/BEGIN CERTIFICATE/,/END CERT
/p' | openssl x509 -text 2>/dev/null | sed -n 's/ *Not After : *//p'"

app = Flask(__name__)

def vault():
    end_date = check_output(vault_string,shell='true').strip()
    end_date_seconds = parser.parse(end_date).timestamp()
    now_seconds = int(datetime.now().strftime("%s"))
    days_to_expire = (end_date_seconds - now_seconds) / 24 / 3600
    return str(int(days_to_expire))

def proxy_inj():
    end_date = check_output(proxy_inj_string,shell='true').strip()
    end_date_seconds = parser.parse(end_date).timestamp()
    now_seconds = int(datetime.now().strftime("%s"))
    days_to_expire = (end_date_seconds - now_seconds) / 24 / 3600
    return str(int(days_to_expire))


if vault_enabled == 'true' or vault_enabled == 'True' :
    @app.route('/vault-cert', methods=['GET'])
    def ssl_monitor_vault():
        return vault()

if proxy_injector_enabled == 'true' or proxy_injector_enabled == 'True':
    @app.route('/proxy-inj-cert', methods=['GET'])
    def ssl_monitor_proxy_inj():
        return proxy_inj()


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
