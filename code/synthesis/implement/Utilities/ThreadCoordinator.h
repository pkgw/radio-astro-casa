// -*- C++ -*-
//# ThreadCoordinator.h: Definition of the ThreadCoordinator class
//# Copyright (C) 1997,1998,1999,2000,2001,2002,2003
//# Associated Universities, Inc. Washington DC, USA.
//#
//# This library is free software; you can redistribute it and/or modify it
//# under the terms of the GNU Library General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or (at your
//# option) any later version.
//#
//# This library is distributed in the hope that it will be useful, but WITHOUT
//# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
//# License for more details.
//#
//# You should have received a copy of the GNU Library General Public License
//# along with this library; if not, write to the Free Software Foundation,
//# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
//#
//# Correspondence concerning AIPS++ should be addressed as follows:
//#        Internet email: aips2-request@nrao.edu.
//#        Postal address: AIPS++ Project Office
//#                        National Radio Astronomy Observatory
//#                        520 Edgemont Road
//#                        Charlottesville, VA 22903-2475 USA
//#
//# $Id$

#include <casa/aips.h>
#include <casa/aipstype.h>
#include <cstddef>

//<example>
//
// Code in the master thread:
//
//    ThreadCoordinator threadCoordinator (nThreads);
//
//    // Create nThread threads and pass them a pointer to the thread coordinator
//    // object.  Then enter the work loop
//    
//    for (int i = 0; i < nBuffers; i++){
//    
//      // Provide access to the i-th buffer
//    
//      threadCoordinator->getToWork(& vb); // tell workers to hop to it!
//                                          // blocks if workers still busy
//    
//     }
//    
// Code in each worker thread:
//    
//    while (True){
//    
//      VisBuffer * workingBuffer = threadCoordinator_p->waitForWork (this);
//      if (workingBuffer == NULL)
//        break;
//    
//      doSomeWork(workingBuffer);
//     }
// </example>

#ifndef SYNTHESIS_THREADCOORDINATOR_H
#define SYNTHESIS_THREADCOORDINATOR_H

namespace boost {
    class barrier;
};

namespace casa {

namespace async {
  class Condition;
  class Mutex;
  class Thread;
}

class String;
class VisBuffer;

class ThreadCoordinatorBase {

public:

  virtual ~ThreadCoordinatorBase ();

  void waitForWorkersToFinishTask ();

protected:

  ThreadCoordinatorBase (Int nThreads, bool logStates);


  void dispatchWork ();
  void getToWork ();
  virtual void installWorkInfo () = 0;
  bool waitForWork (const async::Thread * thisThread);
  void waitForWorkersToReport ();


private:

  boost::barrier * barrier_p;
  bool logStates_p;
  async::Mutex * mutex_p;
  Int nThreads_p;
  volatile Int nThreadsAtBarrier_p;
  volatile Int nThreadsDispatched_p;
  volatile Bool readyForWork_p;
  async::Condition * stateChanged_p;
  const VisBuffer * vb_p;
  volatile bool workCompleted_p;
  volatile bool workToBeDone_p;

  void logState (const String & tag) const;

};

template <typename T>
class ThreadCoordinator : public ThreadCoordinatorBase {

public:

    ThreadCoordinator (Int nThreads, Bool logStates = False) : ThreadCoordinatorBase (nThreads, logStates) {}

    void
    giveWorkToWorkers (T * workInfo)
    {
        workInfoInWaiting_p = workInfo;
        waitForWorkersToReport ();
        dispatchWork ();
    }

    void
    getToWork (T * workInfo)
    {
        workInfoInWaiting_p = workInfo;
        ThreadCoordinatorBase::getToWork ();
    }

    T *
    waitForWork (const async::Thread * thisThread)
    {
        bool ok = ThreadCoordinatorBase::waitForWork (thisThread);
        T * result = ok ? workInfo_p : NULL;

        return result;
    }

protected:

    void
    installWorkInfo ()
    {
        workInfo_p = workInfoInWaiting_p;
        workInfoInWaiting_p = NULL;
    }


private:

    T * workInfoInWaiting_p;
    T * workInfo_p;
};

} // end namespace casa
#endif // 
