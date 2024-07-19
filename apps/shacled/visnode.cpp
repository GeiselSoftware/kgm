#include "visnode.h"

int VisNode::last_node_id = 1;

int VisNode::get_next_id()
{
  return last_node_id++;
}

VisNode::VisNode(int new_node_id, const URI& node_uri)
{
  this->node_uri = node_uri;
  this->ID = new_node_id;
}

VisNode::~VisNode()
{
}
