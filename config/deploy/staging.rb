role :be,                         'riovlb244.globoi.com', 'riovlb245.globoi.com'
role :filer,                      'filer.staging.globoi.com'

# Hosts
set :barramento_backstage_host,   'barramento.backstage.globoi.com'
set :filer_host,                  'riofb01a'
set :redis_host,                  'redis.brainiak.globoi.com'
set :syslog_host,                 'syslog.tcp.glog.globoi.com'
set :elasticsearch_host,          'esearch.globoi.com'

# Ports
set :redis_port,                  20019

# Variables
set :puppetmaster_env,            'staging'
set :redis_password,              '4fdfa56255f21ccf01b3d78f999caea3'

# Directories
set :dbpasswd_dir,                "/mnt/projetos/dbpasswd/#{projeto}"

# Files
set :log_filepath,                '/opt/logs/brainiak/gunicorn-be/gunicorn-be.log'
set :triplestore_config_filepath, "#{dbpasswd_dir}/triplestore.ini"
