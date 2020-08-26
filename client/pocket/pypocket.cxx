#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include "pocket_dispatcher.h"

void translate_LookupNodeException(LookupNodeException const& e)
{
	PyErr_SetString(PyExc_RuntimeError, e.what());
}

void translate_NodeNotFileException(NodeNotFileException const& e)
{
	PyErr_SetString(PyExc_RuntimeError, e.what());
}

void translate_OpenLocalFileError(OpenLocalFileError const& e)
{
	PyErr_SetString(PyExc_RuntimeError, e.what());
}

BOOST_PYTHON_MODULE(libpocket)
{
	using namespace boost::python;
	class_<std::vector<std::string> >("StringVec")
                .def(vector_indexing_suite<std::vector<std::string> >());

	register_exception_translator<LookupNodeException>(&translate_LookupNodeException);
	register_exception_translator<NodeNotFileException>(&translate_NodeNotFileException);
	register_exception_translator<OpenLocalFileError>(&translate_OpenLocalFileError);
	class_<PocketDispatcher>("PocketDispatcher")
		.def("Initialize", &PocketDispatcher::Initialize)
		.def("MakeDir", &PocketDispatcher::MakeDir)
		.def("Lookup", &PocketDispatcher::Lookup)
		.def("Enumerate", &PocketDispatcher::Enumerate)
		.def("EnumerateWithReturn", &PocketDispatcher::EnumerateWithReturn)
		.def("PutFile", &PocketDispatcher::PutFile)
		.def("GetFile", &PocketDispatcher::GetFile)
		.def("DeleteFile", &PocketDispatcher::DeleteFile)
		.def("DeleteDir", &PocketDispatcher::DeleteDir)
		.def("PutBuffer", &PocketDispatcher::PutBuffer)
		.def("GetBuffer", &PocketDispatcher::GetBuffer)
		.def("GetBufferBytes", &PocketDispatcher::GetBufferBytes)
		.def("CountFiles", &PocketDispatcher::CountFiles);
}