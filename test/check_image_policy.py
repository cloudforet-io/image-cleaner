import unittest
import fnmatch

def _check_image_policy(image_name, rule):
    if rule['name'][:1] == "!":
        return not fnmatch.fnmatch(image_name, rule['name'][1:])
    else:
        return fnmatch.fnmatch(image_name, rule['name'])

class CheckImagePolicy(unittest.TestCase):
    def setUp(self) -> None:
        self.image_names = ['aws-cloud-services', 'console', 'spot-automation', 'inventory', 'console-api', 'build',
                            'supervisor', 'monitoring', 'aws-ec2', 'console-assets', 'azure-cloud-services', 'identity',
                            'docs', 'statistics', 'cost-saving', 'azure-vm', 'plugin', 'repository', 'notification',
                            'google-cloud-services', 'report', 'secret', 'config', 'power-scheduler', 'spacectl',
                            'billing', 'aws-cloudtrail', 'aws-cloudwatch', 'google-cloud-compute', 'project-site',
                            'oracle-cloud-services', 'googleoauth2', 'google-cloud-stackdriver',
                            'google-cloud-power-controller', 'aws-trusted-advisor', 'azure-power-state',
                            'monitoring-metric-collector', 'aws-power-state', 'google-cloud-power-state', 'gcp-compute',
                            'aws-personal-health-dashboard', 'azure-monitor', 'aws-health', 'azure-power-controller',
                            'aws-power-controller', 'kubectl-proxy', 'plugin-aws-sns-monitoring-webhook',
                            'plugin-grafana-monitoring-webhook', 'gcp-cloud-services', 'plugin-email-noti-protocol',
                            'aws-price-info', 'plugin-amorepacific-monitoring-webhook', 'aws-summary',
                            'plugin-azure-cloud-service-inven-collector', 'alibaba-cloud-ecs',
                            'voicecall-notification-protocol', 'plugin-megazone-sms-notification-protocol',
                            'plugin-telegram-notification-protocol', 'aws-spot-automation-controller',
                            'plugin-aws-ec2-inven-collector', 'plugin-megazone-voicecall-notification-protocol',
                            'tester', 'helm-test', 'plugin-grafana-mon-webhook', 'plugin-slack-notification-protocol',
                            'aws-network', 'server-mockup', 'plugin-telegram-noti-protocol',
                            'plugin-aws-sns-mon-webhook', 'aws-power-scheduler-controller', 'plugin-kbfg-identity-auth',
                            'plugin-aws-trusted-advisor-inven-collector', 'plugin-slack-noti-protocol',
                            'plugin-keycloak-identity-auth', 'plugin-keycloak-oidc',
                            'plugin-monitoring-metric-inven-collector', 'plugin-zabbix-mon-webhook',
                            'plugin-mzc-voicecall-noti-protocol', 'plugin-aws-cloudwatch-mon-datasource',
                            'plugin-azure-monitor-mon-datasource', 'plugin-aws-cloud-service-inven-collector',
                            'plugin-aws-phd-inven-collector', 'plugin-alibaba-cloud-ecs-inven-collector',
                            'plugin-aws-spot-controller', 'plugin-google-cloud-state-inven-collector',
                            'plugin-azure-state-inven-collector', 'plugin-azure-vm-inven-collector',
                            'plugin-google-stackdriver-mon-datasource', 'plugin-google-cloud-compute-inven-collector',
                            'plugin-google-cloud-service-inven-collector', 'plugin-aws-ps-controller',
                            'plugin-googleoauth2-identity-auth', 'aws-trustedadvisor', 'spot-automation-proxy',
                            'plugin-email-notification-protocol', 'plugin-oracle-cloud-service-inven-collector',
                            'plugin-azure-ps-controller', 'plugin-amorepacific-mon-webhook',
                            'spot-automation-proxy-nginx', 'plugin-aws-state-inven-collector']

        self.image_names_not_contain_plugin = ['aws-cloud-services', 'console', 'spot-automation', 'inventory',
                                               'console-api', 'build', 'supervisor', 'monitoring', 'aws-ec2',
                                               'console-assets', 'azure-cloud-services', 'identity', 'docs',
                                               'statistics', 'cost-saving', 'azure-vm', 'plugin', 'repository',
                                               'notification', 'google-cloud-services', 'report', 'secret', 'config',
                                               'power-scheduler', 'spacectl', 'billing', 'aws-cloudtrail',
                                               'aws-cloudwatch', 'google-cloud-compute', 'project-site',
                                               'oracle-cloud-services', 'googleoauth2', 'google-cloud-stackdriver',
                                               'google-cloud-power-controller', 'aws-trusted-advisor',
                                               'azure-power-state', 'monitoring-metric-collector', 'aws-power-state',
                                               'google-cloud-power-state', 'gcp-compute',
                                               'aws-personal-health-dashboard', 'azure-monitor', 'aws-health',
                                               'azure-power-controller', 'aws-power-controller', 'kubectl-proxy',
                                               'gcp-cloud-services', 'aws-price-info', 'aws-summary',
                                               'alibaba-cloud-ecs', 'voicecall-notification-protocol',
                                               'aws-spot-automation-controller', 'tester', 'helm-test', 'aws-network',
                                               'server-mockup', 'aws-power-scheduler-controller', 'aws-trustedadvisor',
                                               'spot-automation-proxy', 'spot-automation-proxy-nginx']

        self.image_only_plugin = ['plugin-aws-sns-monitoring-webhook', 'plugin-grafana-monitoring-webhook',
                                  'plugin-email-noti-protocol', 'plugin-amorepacific-monitoring-webhook',
                                  'plugin-azure-cloud-service-inven-collector',
                                  'plugin-megazone-sms-notification-protocol', 'plugin-telegram-notification-protocol',
                                  'plugin-aws-ec2-inven-collector', 'plugin-megazone-voicecall-notification-protocol',
                                  'plugin-grafana-mon-webhook', 'plugin-slack-notification-protocol',
                                  'plugin-telegram-noti-protocol', 'plugin-aws-sns-mon-webhook',
                                  'plugin-kbfg-identity-auth', 'plugin-aws-trusted-advisor-inven-collector',
                                  'plugin-slack-noti-protocol', 'plugin-keycloak-identity-auth', 'plugin-keycloak-oidc',
                                  'plugin-monitoring-metric-inven-collector', 'plugin-zabbix-mon-webhook',
                                  'plugin-mzc-voicecall-noti-protocol', 'plugin-aws-cloudwatch-mon-datasource',
                                  'plugin-azure-monitor-mon-datasource', 'plugin-aws-cloud-service-inven-collector',
                                  'plugin-aws-phd-inven-collector', 'plugin-alibaba-cloud-ecs-inven-collector',
                                  'plugin-aws-spot-controller', 'plugin-google-cloud-state-inven-collector',
                                  'plugin-azure-state-inven-collector', 'plugin-azure-vm-inven-collector',
                                  'plugin-google-stackdriver-mon-datasource',
                                  'plugin-google-cloud-compute-inven-collector',
                                  'plugin-google-cloud-service-inven-collector', 'plugin-aws-ps-controller',
                                  'plugin-googleoauth2-identity-auth', 'plugin-email-notification-protocol',
                                  'plugin-oracle-cloud-service-inven-collector', 'plugin-azure-ps-controller',
                                  'plugin-amorepacific-mon-webhook', 'plugin-aws-state-inven-collector']

    def test_not_contain_plugin(self):
        rule = {'name': '!plugin-*'}
        for i,image_name in enumerate(self.image_names_not_contain_plugin):
            with self.subTest(i=i):
                check = _check_image_policy(image_name,rule)
                self.assertTrue(check)

    def test_only_plugin(self):
        rule = {'name': 'plugin-*'}
        for i,image_name in enumerate(self.image_only_plugin):
            with self.subTest(i=i):
                check = _check_image_policy(image_name,rule)
                self.assertTrue(check)