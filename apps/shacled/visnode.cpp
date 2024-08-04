#include "visnode.h"
#include "vis-manager.h"

unsigned long int VisNode::last_node_id = 1;

unsigned long int VisNode::get_next_id()
{
  return last_node_id++;
}

VisNode::VisNode(VisManager* vis_man)
{
  this->vis_man = vis_man;
  this->rdf_man = vis_man->rdf_man;
}

VisNode::~VisNode()
{
}

