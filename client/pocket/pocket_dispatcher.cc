/*
 * CppCrail: Native Crail
 *
 * Author: Patrick Stuedi  <stu@zurich.ibm.com>
 *
 * Copyright (C) 2015-2018, IBM Corporation
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "pocket_dispatcher.h"

#include <iostream>
#include <string.h>
#include <boost/python.hpp>

#include "crail_directory.h"
#include "crail_file.h"
#include "crail_outputstream.h"

using namespace std;

PocketDispatcher::PocketDispatcher() {}

PocketDispatcher::~PocketDispatcher() {}

int PocketDispatcher::Initialize(string address, int port) {
  return this->crail_.Initialize(address, port);
}

int PocketDispatcher::MakeDir(string name) {
  unique_ptr<CrailNode> crail_node =
      crail_.Create(name, FileType::Directory, 0, 0, true);
  if (!crail_node) {
    throw std::runtime_error("makedir failed");
  }
  return 0;
}

int PocketDispatcher::Lookup(string name) {
  unique_ptr<CrailNode> crail_node = crail_.Lookup(name);
  if (!crail_node) {
    throw LookupNodeException();
  }
  return 0;
}

int PocketDispatcher::Enumerate(string name) {
  unique_ptr<CrailNode> crail_node = crail_.Lookup(name);
  if (!crail_node) {
    throw LookupNodeException();
  }
  if (crail_node->type() != static_cast<int>(FileType::Directory)) {
    throw std::runtime_error("node is not a directory");
  }

  CrailNode *node = crail_node.get();
  CrailDirectory *directory = static_cast<CrailDirectory *>(node);
  directory->Enumerate();
  return 0;
}

std::vector<string> PocketDispatcher::EnumerateWithReturn(string name) {
  unique_ptr<CrailNode> crail_node = crail_.Lookup(name);
  if (!crail_node) {
    throw LookupNodeException();
  }
  if (crail_node->type() != static_cast<int>(FileType::Directory)) {
    throw std::runtime_error("node is not a directory");
  }

  CrailNode *node = crail_node.get();
  CrailDirectory *directory = static_cast<CrailDirectory *>(node);
  auto content = directory->EnumerateWithReturn();
  return content;
}

int PocketDispatcher::PutFile(string local_file, string dst_file,
                              bool enumerable) {
  FILE *fp = fopen(local_file.c_str(), "r");
  if (!fp) {
    throw OpenLocalFileError(local_file);
  }

  unique_ptr<CrailNode> crail_node =
      crail_.Create(dst_file, FileType::File, 0, 0, enumerable);
  if (!crail_node) {
    throw LookupNodeException();
  }
  if (crail_node->type() != static_cast<int>(FileType::File)) {
    throw NodeNotFileException();
  }

  CrailNode *node = crail_node.get();
  CrailFile *file = static_cast<CrailFile *>(node);
  unique_ptr<CrailOutputstream> outputstream = file->outputstream();

  shared_ptr<ByteBuffer> buf = make_shared<ByteBuffer>(kBufferSize);
  while (size_t len = fread(buf->get_bytes(), 1, buf->remaining(), fp)) {
    buf->set_position(buf->position() + len);
    if (buf->remaining() > 0) {
      continue;
    }

    buf->Flip();
    while (buf->remaining() > 0) {
      if (outputstream->Write(buf) < 0) {
        return -1;
      }
    }
    buf->Clear();
  }

  if (buf->position() > 0) {
    buf->Flip();
    while (buf->remaining() > 0) {
      if (outputstream->Write(buf) < 0) {
        return -1;
      }
    }
  }

  fclose(fp);
  outputstream->Close();

  return 0;
}

int PocketDispatcher::GetFile(string src_file, string local_file) {
  unique_ptr<CrailNode> crail_node = crail_.Lookup(src_file);
  if (!crail_node) {
    throw LookupNodeException();
  }
  if (crail_node->type() != static_cast<int>(FileType::File)) {
    throw NodeNotFileException();
  }

  FILE *fp = fopen(local_file.c_str(), "w");
  if (!fp) {
    throw OpenLocalFileError(local_file);
  }

  CrailNode *node = crail_node.get();
  CrailFile *file = static_cast<CrailFile *>(node);
  unique_ptr<CrailInputstream> inputstream = file->inputstream();

  shared_ptr<ByteBuffer> buf = make_shared<ByteBuffer>(kBufferSize);
  while (inputstream->Read(buf) > 0) {
    buf->Flip();
    while (buf->remaining()) {
      if (size_t len = fwrite(buf->get_bytes(), 1, buf->remaining(), fp)) {
        buf->set_position(buf->position() + len);
      } else {
        break;
      }
    }
    buf->Clear();
  }
  fclose(fp);
  inputstream->Close();

  return 0;
}

int PocketDispatcher::DeleteDir(string directory) {
  return crail_.Remove(directory, true);
}

int PocketDispatcher::DeleteFile(string file) {
  return crail_.Remove(file, false);
}

int PocketDispatcher::CountFiles(string directory) {
  int op = 5;
  return crail_.Ioctl((unsigned char)op, directory);
}

int PocketDispatcher::PutBuffer(string input_data, string dst_file,
                                bool enumerable) {
  const char* data = input_data.data();
  int len = input_data.size();
  unique_ptr<CrailNode> crail_node =
      crail_.Create(dst_file, FileType::File, 0, 0, enumerable);
  if (!crail_node) {
    throw LookupNodeException();
  }
  if (crail_node->type() != static_cast<int>(FileType::File)) {
    throw NodeNotFileException();
  }

  CrailNode *node = crail_node.get();
  CrailFile *file = static_cast<CrailFile *>(node);
  unique_ptr<CrailOutputstream> outputstream = file->outputstream();

  shared_ptr<ByteBuffer> buf = make_shared<ByteBuffer>(len);
  buf->PutBytes(data, len);
  buf->Flip();
  while (buf->remaining() > 0) {
    if (outputstream->Write(buf) < 0) {
      return -1;
    }
  }
  outputstream->Close();

  return 0;
}

int PocketDispatcher::GetBuffer(char data[], int len, string src_file) {
  unique_ptr<CrailNode> crail_node = crail_.Lookup(src_file);
  if (!crail_node) {
    throw LookupNodeException();
  }
  if (crail_node->type() != static_cast<int>(FileType::File)) {
    throw NodeNotFileException();
  }

  CrailNode *node = crail_node.get();
  CrailFile *file = static_cast<CrailFile *>(node);
  unique_ptr<CrailInputstream> inputstream = file->inputstream();

  shared_ptr<ByteBuffer> buf = make_shared<ByteBuffer>(len);
  while (buf->remaining()) {
    if (inputstream->Read(buf) < 0) {
      return -1;
    }
  }
  buf->Clear();
  memcpy(data, buf->get_bytes(), len);

  inputstream->Close();

  return 0;
}

boost::python::object PocketDispatcher::GetBufferBytes(string src_file) {
  namespace python = boost::python;
  unique_ptr<CrailNode> crail_node = crail_.Lookup(src_file);
  if (!crail_node) {
    throw LookupNodeException();
  }
  if (crail_node->type() != static_cast<int>(FileType::File)) {
    throw NodeNotFileException();
  }

  CrailNode *node = crail_node.get();
  CrailFile *file = static_cast<CrailFile *>(node);
  unique_ptr<CrailInputstream> inputstream = file->inputstream();

  string output;
  shared_ptr<ByteBuffer> buf = make_shared<ByteBuffer>(kBufferSize);
  while (inputstream->Read(buf) > 0) {
    buf->Flip();
    output.append(reinterpret_cast<char*>(buf->get_bytes()), buf->size());
    buf->Clear();
  }
  inputstream->Close();
  PyObject* py_object = PyBytes_FromStringAndSize(output.data(), output.size());
  python::handle<> handle(py_object);
  return python::object(handle);
}
