#include "node.h"

int Node::last_node_id = 1;

int Node::get_next_id()
{
  return last_node_id++;
}

Node::Node(int new_node_id)
{
  this->ID = new_node_id;
}

Node::~Node()
{
}

