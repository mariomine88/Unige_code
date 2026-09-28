#!/bin/bash

current_tag="teaa:test3"

docker build --tag ${current_tag} --force-rm .

docker tag ${current_tag} jonander/${current_tag}


echo ""
echo "TO DO:"
echo ""
echo "  docker push jonander/${current_tag} "
echo ""
