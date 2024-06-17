// -*- c++ -*-
#pragma once

#include <memory>

// Dict<string, string>
template <class K, class V> class Dict
{
public:
  bool has_key(const K&) const;
  V* set(const K& k, const V&);
  V* set(const K& k);

  V* get(const K& k);
  const V* get(const K& k) const;
};

// Dict<URIRef, shared_ptr<Node>>
template <class K, class V> class Dict<K, std::shared_ptr<V>>
{
private:
  std::map<K, std::shared_ptr<V>> m;
  
public:
  bool has_key(const K&) const;
  std::shared_ptr<V> set(const K& k, std::shared_ptr<V>);
  std::shared_ptr<V> set(const K&);

  std::shared_ptr<V> get(const K&);
  //std::shared_ptr<V> get(const K&) const;
  template <class DV> std::shared_ptr<DV> get(const K&);
  
  std::vector<K> keys() const;
  
  typename decltype(m)::iterator begin() { return this->m.begin(); }
  typename decltype(m)::iterator end() { return this->m.end(); }
};

template <class K, class V>
inline bool Dict<K, std::shared_ptr<V>>::has_key(const K& key) const
{
  return this->m.find(key) != this->m.end();
}

template <class K, class V>
inline std::vector<K> Dict<K, std::shared_ptr<V>>::keys() const
{
  std::vector<K> ret;
  for (const auto& [k, _]: this->m) {
    ret.push_back(k);
  }
  return ret;
}

template <class K, class V>
inline std::shared_ptr<V> Dict<K, std::shared_ptr<V>>::set(const K& key, std::shared_ptr<V> v)
{
  auto [it, res] = this->m.insert_or_assign(key, v);
  return (*it).second;
}

template <class K, class V>
inline std::shared_ptr<V> Dict<K, std::shared_ptr<V>>::set(const K& key)
{
  auto [it, res] = this->m.insert_or_assign(key, std::shared_ptr<V>());
  return (*it).second;
}

template <class K, class V>
inline std::shared_ptr<V> Dict<K, std::shared_ptr<V>>::get(const K& key)
{
  auto it = this->m.find(key);
  return it == this->m.end() ? std::shared_ptr<V>() : (*it).second;
}

template <class K, class V>
template <class DV>
inline std::shared_ptr<DV> Dict<K, std::shared_ptr<V>>::get(const K& key)
{
  auto it = this->m.find(key);
  auto ret = it == this->m.end() ? std::shared_ptr<V>() : (*it).second;
  return std::dynamic_pointer_cast<DV>(ret);  
}

