role :be,                         'cittavld45.globoi.com'
role :filer,                      'filer.qa01.globoi.com'

# Hosts
set :barramento_baas_host,        'barramento.baas.qa01.globoi.com'
set :filer_host,                  'riofd06'
set :redis_host,                  'redis.qa01.globoi.com'
set :syslog_host,                 'syslog.tcp.glog.qa01.globoi.com'
set :virtuoso_host,               'qa1.virtuoso.globoi.com'

# Ports
set :redis_port,                  20015
set :virtuoso_port,               8890

# URLs
set :virtuoso_url,                "http://#{virtuoso_host}:#{virtuoso_port}/sparql-auth"

# Variables
set :puppetmaster_env,            'qa1'
set :redis_password,              'a8pdifs2e2m9afn7tcifcea99674aad2'

# Directories
set :dbpasswd_dir,                '/mnt/projetos/dbpasswd/#{projeto}'

# Files
set :log_filepath,                '/opt/logs/brainiak/gunicorn-be/gunicorn-be.log'
set :triplestore_config_filepath, "#{dbpasswd_dir}/config.ini"
