// -*- c++ -*-
#pragma once

#include <nlohmann/json.hpp>
#include <lib-utils/rdf-utils.h>

namespace fuseki {
  RDFSPO rdf_parse_binding(const nlohmann::json& binding);
}
