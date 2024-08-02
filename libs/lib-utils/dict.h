// -*- c++ -*-
#pragma once

#include <map>
#include <memory>

// Dict<string, string>
template <class K, class V> class Dict
{
private:
  std::map<K, V> m;
  
public:
  void clear() { m.clear(); }
  bool has_key(const K& k) const { return m.find(k) != m.end(); }
  V* set(const K& k, const V& v) { auto [it, _] = this->m.insert_or_assign(k, v); return &(*it).second; }
  V* set(const K& k) { auto [it, _] = this->m.insert_or_assign(k, V()); return &(*it).second; }

  V* get(const K& k) { auto it = m.find(k); return it == m.end() ? 0 : &(*it).second; }  
  //const V* get(const K& k) const;

  bool remove(const K& k) { return m.erase(k) == 1; } // true if element was removed
  
  std::vector<K> keys() const { std::vector<K> ret; for (const auto& [k, _]: m) { ret.push_back(k); } return ret; }
  
  typename decltype(m)::iterator begin() { return this->m.begin(); }
  typename decltype(m)::iterator end() { return this->m.end(); }  
};

template <class K, class V> class Dict<K, V*>
{
private:
  std::map<K, V*> m;

public:
  void clear() { m.clear(); }
  bool has_key(const K& k) const { return m.find(k) != m.end(); }
  V* set(const K& k, V* v) { auto [it, _] = this->m.insert_or_assign(k, v); return (*it).second; }
  V* set(const K& k) { auto [it, _] = this->m.insert_or_assign(k, 0); return (*it).second; }

  V* get(const K& k) { auto it = m.find(k); return it == m.end() ? 0 : (*it).second; }  
  //std::shared_ptr<V> get(const K&) const;
  template <class DV> DV* get(const K& k) { auto it = m.find(k); return dynamic_cast<DV*>(it == m.end() ? 0 : (*it).second); }

  bool remove(const K& k) { return m.erase(k) == 1; } // true if element was removed

  std::vector<K> keys() const { std::vector<K> ret; for (const auto& [k, _]: m) { ret.push_back(k); } return ret; }
  
  typename decltype(m)::iterator begin() { return this->m.begin(); }
  typename decltype(m)::iterator end() { return this->m.end(); }  
};

// Dict<URIRef, shared_ptr<Node>>
template <class K, class V> class Dict<K, std::shared_ptr<V>>
{
private:
  std::map<K, std::shared_ptr<V>> m;
  
public:
  void clear() { m.clear(); }
  bool has_key(const K& k) const { return m.find(k) != m.end(); }
  std::shared_ptr<V> set(const K& k, std::shared_ptr<V> v) { auto [it, _] = this->m.insert_or_assign(k, v); return (*it).second; }
  std::shared_ptr<V> set(const K& k) { auto [it, _] = this->m.insert_or_assign(k, std::shared_ptr<V>()); return (*it).second; }

  std::shared_ptr<V> get(const K& k) { auto it = m.find(k); return it == m.end() ? std::shared_ptr<V>() : (*it).second; }  
  //std::shared_ptr<V> get(const K&) const;
  template <class DV> std::shared_ptr<DV> get(const K& k) { auto it = m.find(k); return std::dynamic_pointer_cast<DV>(it == m.end() ? std::shared_ptr<V>() : (*it).second); }

  bool remove(const K& k) { return m.erase(k) == 1; } // true if element was removed
  
  std::vector<K> keys() const { std::vector<K> ret; for (const auto& [k, _]: m) { ret.push_back(k); } return ret; }
  
  typename decltype(m)::iterator begin() { return this->m.begin(); }
  typename decltype(m)::iterator end() { return this->m.end(); }
};

