
#include <memory>

/* Using the PyCXX API for C++ Python integration
 * It is extremely convenient and avoids the need to write boilerplate
 * code for handling the Python reference counts.
 * It is licensed under BSD terms compatible with reSIProcate */
#include <Python.h>
#include <CXX/Objects.hxx>

#include "rutil/Logger.hxx"
#include "resip/stack/Helper.hxx"
#include "repro/Dispatcher.hxx"
#include "repro/Plugin.hxx"
#include "repro/Processor.hxx"
#include "repro/Proxy.hxx"
#include "repro/RequestContext.hxx"

#include "PyRouteWorker.hxx"
#include "PyThreadSupport.hxx"

#define RESIPROCATE_SUBSYSTEM resip::Subsystem::REPRO

using namespace resip;
using namespace repro;

static PyMethodDef PyRouteMethods[] = {
  {NULL, NULL, 0, NULL}
};

class PyRoutePlugin : public Plugin, public Processor
{
   public:
      PyRoutePlugin() : Processor("PyRoute"), mThreadState(0), mDispatcher(0) {};
      ~PyRoutePlugin()
      {
         if(mDispatcher)
         {
            DebugLog(<<"Deleting dispatcher for worker threads");
            delete mDispatcher;
         }
         if(mThreadState)
         {
            PyEval_RestoreThread(mThreadState);
            // this can take time as it de-initializes all Python state
            DebugLog(<<"Calling Py_Finalize");
            Py_Finalize();
            DebugLog(<<"Py_Finalize is done");
         }
      };

      virtual bool init(SipStack& sipStack, ProxyConfig *proxyConfig)
      {
         DebugLog(<<"PyRoutePlugin: init called");

         if(!proxyConfig)
         {
            ErrLog(<<"proxyConfig == 0, aborting");
            return false;
         }

         Data pyPath(proxyConfig->getConfigData("PyRoutePath", "", true));
         Data routeScript(proxyConfig->getConfigData("PyRouteScript", "", true));
         if(pyPath.empty())
         {
            ErrLog(<<"PyRoutePath not specified in config, aborting");
            return false;
         }
         if(routeScript.empty())
         {
            ErrLog(<<"PyRouteScript not specified in config, aborting");
            return false;
         }

         // FIXME: what if there are other Python modules?
         Py_Initialize();
         PyEval_InitThreads();
         Py_InitModule("pyroute", PyRouteMethods);
         PyObject *sys_path = PySys_GetObject("path");
         PyObject *addpath = PyString_FromString(pyPath.c_str());
         PyList_Append(sys_path, addpath);
         mThreadState = PyGILState_GetThisThreadState();

         PyObject *pyModule = PyImport_ImportModule(routeScript.c_str());
         if(!pyModule)
         {
            ErrLog(<<"Failed to load module "<< routeScript);
            return false;
         }
         mPyModule.reset(new Py::Module(pyModule));

         if(mPyModule->getDict().hasKey("on_load"))
         {
            DebugLog(<< "found on_load method, trying to invoke it...");
            try
            {
               StackLog(<< "invoking on_load");
               mPyModule->callMemberFunction("on_load");
            }
            catch (const Py::Exception& ex)
            {
               DebugLog(<< "call to on_load method failed: " << Py::value(ex));
               StackLog(<< Py::trace(ex));
               return false;
            }
         } 

         mAction = mPyModule->getAttr("provide_route");

         PyInterpreterState* interpreterState = mThreadState->interp;
         PyEval_ReleaseThread(mThreadState);

         int numPyRouteWorkerThreads = proxyConfig->getConfigInt("PyRouteNumWorkerThreads", 2);
         std::auto_ptr<Worker> worker(new PyRouteWorker(interpreterState, mAction));
         mDispatcher = new Dispatcher(worker, &sipStack, numPyRouteWorkerThreads);

         return true;
      }

      virtual void onRequestProcessorChainPopulated(ProcessorChain& chain)
      {
         DebugLog(<<"PyRoutePlugin: onRequestProcessorChainPopulated called");

         // The module class is also the monkey class, no need to create
         // any monkey instance here

         // Add the pyroute monkey to the chain
         chain.addProcessor(std::auto_ptr<Processor>(this));
      }

      virtual void onResponseProcessorChainPopulated(ProcessorChain& chain)
      {
         DebugLog(<<"PyRoutePlugin: onResponseProcessorChainPopulated called");
      }

      virtual void onTargetProcessorChainPopulated(ProcessorChain& chain)
      {
         DebugLog(<<"PyRoutePlugin: onTargetProcessorChainPopulated called");
      }

      /*
       * Now we implemented the Processor API from repro/Processor.hxx
       */

      virtual processor_action_t process(RequestContext &context)
      {
         DebugLog(<< "Monkey handling request: PyRoute");

         // Has the work been done already?
         PyRouteWork* work = dynamic_cast<PyRouteWork*>(context.getCurrentEvent());
         if(work)
         {
            for(
               std::vector<Data>::iterator i = work->mTargets.begin();
               i != work->mTargets.end();
               i++)
            {
               context.getResponseContext().addTarget(NameAddr(*i));
            }
            return Processor::Continue;
         }

         SipMessage& msg = context.getOriginalRequest();
         if(msg.method() != INVITE && msg.method() != MESSAGE)
         {
            // We only route INVITE and MESSAGE, otherwise we ignore
            return Processor::Continue;
         }
         work = new PyRouteWork(*this, context.getTransactionId(), &(context.getProxy()), msg);
         std::auto_ptr<ApplicationMessage> app(work);
         mDispatcher->post(app);

         return Processor::WaitingForEvent;
      }

   private:
      PyThreadState* mThreadState;
      std::auto_ptr<Py::Module> mPyModule;
      Py::Callable mAction;
      Dispatcher* mDispatcher;
};


extern "C" {

static
Plugin* instantiate()
{
   return new PyRoutePlugin();
}

ReproPluginDescriptor reproPluginDesc =
{
   REPRO_DSO_PLUGIN_API_VERSION,
   &instantiate
};

};

/* ====================================================================
 *
 * Copyright 2013 Daniel Pocock http://danielpocock.com  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. Neither the name of the author(s) nor the names of any contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR(S) AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR(S) OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * ====================================================================
 *
 *
 */
