# Download and install the MySQL Connector
$mysqlConnectorUrl = "https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-8.0.27.tar.gz"
$mysqlConnectorFile = "mysql-connector-python-8.0.27.tar.gz"
Invoke-WebRequest $mysqlConnectorUrl -OutFile $mysqlConnectorFile
python -m pip install $mysqlConnectorFile
Remove-Item $mysqlConnectorFile
python -m pip install -r ../requirements.txt