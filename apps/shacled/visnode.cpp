#include "visnode.h"
#include <lib-utils/uuid.h>

unsigned long int VisNode::last_node_id = 1;

unsigned long int VisNode::get_next_id()
{
  return last_node_id++;
}

VisNode::VisNode(ed::NodeId new_node_id, VisManager* vis_man)
{
  this->vis_node_id.vis_node_id = generate_uuid_v4();
  this->ID = new_node_id;
  this->vis_man = vis_man;
}

VisNode::~VisNode()
{
}

void URIVisRep::set(const CURIE& new_curie) {
  this->prev_curie = this->curie;
  this->curie = new_curie;
}
