// -*- c++ -*-

///////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////
////////////////////   NO-THREAD    ///////////////////////////////////////
///////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////

// Tell SWIG to NOT wrap wrappers with our thread protection 

// Deletes any previously defined handler
//SWIGDEBUG  %exception  NO-THREAD
%exception {
$action
}

//SWIGDEBUG  typemap(throws) char * NO-THREAD
%typemap(throws) char * {
	PyErr_SetString(PyExc_RuntimeError, $1);
	SWIG_fail;
}