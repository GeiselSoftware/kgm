#include "visnode.h"

unsigned long int VisNode::last_node_id = 1;

unsigned long int VisNode::get_next_id()
{
  return last_node_id++;
}

VisNode::VisNode(ed::NodeId new_node_id, const URI& node_uri, VisManager* vis_man)
{
  this->node_uri = node_uri;
  this->ID = new_node_id;
  this->vis_man = vis_man;
}

VisNode::~VisNode()
{
}

