kill $(lsof -t -i:$1)
echo "killing all processes running on port $1"

