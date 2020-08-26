#include <boost/python.hpp>
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
	register_exception_translator<LookupNodeException>(&translate_LookupNodeException);
	register_exception_translator<NodeNotFileException>(&translate_NodeNotFileException);
	register_exception_translator<OpenLocalFileError>(&translate_OpenLocalFileError);
	class_<PocketDispatcher>("PocketDispatcher")
		.def("Initialize", &PocketDispatcher::Initialize)
		.def("MakeDir", &PocketDispatcher::MakeDir)
		.def("Lookup", &PocketDispatcher::Lookup)
		.def("Enumerate", &PocketDispatcher::Enumerate)
		.def("PutFile", &PocketDispatcher::PutFile)
		.def("GetFile", &PocketDispatcher::GetFile)
		.def("DeleteFile", &PocketDispatcher::DeleteFile)
		.def("DeleteDir", &PocketDispatcher::DeleteDir)
		.def("PutBuffer", &PocketDispatcher::PutBuffer)
		.def("GetBuffer", &PocketDispatcher::GetBuffer)
		.def("GetBufferBytes", &PocketDispatcher::GetBufferBytes)
		.def("CountFiles", &PocketDispatcher::CountFiles);
}