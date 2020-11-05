#!/bin/bash

ip=$1
n_server=$2
clients_per_server=$3
cycle=$4

if [[ -z $ip ]]
then
    echo 'using default ip: 127.0.0.1'
    ip=127.0.0.1
fi

if [[ -z $n_server ]]
then
    echo 'using default server numer: 1'
    n_server=1
fi

if [[ -z $clients_per_server ]]
then
    echo 'using default clients per server: 1'
    clients_per_server=1
fi

if [[ -z $cycle ]]
then
    echo 'using default cycle 1000'
fi


python start_python_rpc_server.py $n_server &
pid=$!

python profile_client.py $ip $n_server $clients_per_server $cycle

kill $pid
