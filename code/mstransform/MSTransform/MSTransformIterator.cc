//# MSTransformIterator.h: This file contains the implementation of the MSTransformIterator class.
//#
//#  CASA - Common Astronomy Software Applications (http://casa.nrao.edu/)
//#  Copyright (C) Associated Universities, Inc. Washington DC, USA 2011, All rights reserved.
//#  Copyright (C) European Southern Observatory, 2011, All rights reserved.
//#
//#  This library is free software; you can redistribute it and/or
//#  modify it under the terms of the GNU Lesser General Public
//#  License as published by the Free software Foundation; either
//#  version 2.1 of the License, or (at your option) any later version.
//#
//#  This library is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY, without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//#  Lesser General Public License for more details.
//#
//#  You should have received a copy of the GNU Lesser General Public
//#  License along with this library; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston,
//#  MA 02111-1307  USA
//# $Id: $

#include <mstransform/MSTransform/MSTransformIterator.h>

namespace casa
{

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
MSTransformIterator::MSTransformIterator(	vi::VisibilityIterator2 * vi,
											vi::ViImplementation2 * inputVii,
											MSTransformManager *manager):		TransformingVi2 (vi, inputVii)
{

	// TODO (jagonzal): Do we need a copy of the manager here?
	manager_p = manager;

	// Get reference to output (transformed) MS in order to access the SubTables
	transformedMS_p = manager_p->getOutputMs();

	// Create VisBuffer implementation only accessible from this iterator
	buffer_p = new MSTransformBufferImpl(manager_p);

	return;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
MSTransformIterator::~MSTransformIterator()
{
	if (buffer_p != NULL)
	{
		delete buffer_p;
	}

	if (manager_p != NULL)
	{
		String outputMSName = manager_p->getOutputMsName();
		manager_p->close();

		// ~MSTransformManager => ~VisibilityIterator2 => ~VisibilityIteratorImpl2
		delete manager_p;

		Table::relinquishAutoLocks(True);
		Table::deleteTable(outputMSName,True);
	}

	// Now the parent class destructor (~TransformingVi2) is called, which deletes the inner
	// ViImplementation2 object. However it has been already deleted by the MSTRansformManager
	// destructor, so we set it to null here to avoid problems.
	inputVii_p = NULL;

	return;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
void MSTransformIterator::originChunks ()
{
	buffer_p->resetState();
	buffer_p->setRowIdOffset(0);
	getVii()->originChunks();
	return;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
Bool MSTransformIterator::moreChunks () const
{
	buffer_p->resetState();
	Bool res = getVii()->moreChunks();
	return res;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
void MSTransformIterator::nextChunk ()
{
	buffer_p->resetState();
	getVii()->nextChunk();
	return;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
void MSTransformIterator::origin ()
{
	buffer_p->resetState();
	getVii()->origin();
	manager_p->setupBufferTransformations(manager_p->getVisBuffer());
	return;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
Bool MSTransformIterator::more () const
{
	buffer_p->resetState();
	Bool res = getVii()->more();
	if (res)
	{
		manager_p->setupBufferTransformations(manager_p->getVisBuffer());
	}
	return res;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
void MSTransformIterator::next ()
{
	buffer_p->resetState();
	buffer_p->shiftRowIdOffset(manager_p->nRowsToAdd_p);
	getVii()->next();
	return;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
void MSTransformIterator::writeFlag (const Cube<Bool> & flag)
{
	// Get transformed shape
	IPosition transformedShape = manager_p->getShape();

	// Check that user is providing a cube with the right output shape
	if (flag.shape() != transformedShape)
	{
		manager_p->logger_p << LogIO::WARN << LogOrigin("MSTransformIterator", __FUNCTION__)
				<< "Shape of input cube " << flag.shape()
				<< " does not match transformed shape " << transformedShape
				<< LogIO::POST;

		return;
	}

	// Expand channel dimension
	if (manager_p->channelAverage_p)
	{
		Cube<Bool> expandedFlagCube;
		propagateChanAvgFlags(flag,expandedFlagCube);
		manager_p->getVisIter()->writeFlag(expandedFlagCube);

		// Also write FLAG_ROW consistent with FLAG cube
		if (not manager_p->timeAverage_p)
		{
			// Calculate output FLAG_ROW based on expanded flagCube
			// Because we have to take into account also the dropped channels
			Vector<Bool> flagRow;
			calculateFlagRow(expandedFlagCube,flagRow);
			manager_p->getVisIter()->writeFlagRow(flagRow);
		}
	}
	else
	{
		manager_p->getVisIter()->writeFlag(flag);

		// Also write FLAG_ROW consistent with FLAG cube
		if (not manager_p->timeAverage_p)
		{
			// In this case we can use the input flag directly
			Vector<Bool> flagRow;
			calculateFlagRow(flag,flagRow);
			manager_p->getVisIter()->writeFlagRow(flagRow);
		}
	}

	return;
}

// -----------------------------------------------------------------------
//
// -----------------------------------------------------------------------
void MSTransformIterator::writeFlagRow (const Vector<Bool> & rowflags)
{

	// Check that user is providing a row flag vector with the right number of elements
	if (rowflags.size() != manager_p->nRowsToAdd_p)
	{
		manager_p->logger_p << LogIO::WARN << LogOrigin("MSTransformIterator", __FUNCTION__)
				<< "Size of input row flag vector " << rowflags.size()
				<< " does not match number of rows in transformed buffer " <<  manager_p->nRowsToAdd_p
				<< LogIO::POST;

		return;
	}

	manager_p->getVisIter()->writeFlagRow(rowflags);


	if (not manager_p->timeAverage_p)
	{
		// To implement the FLAG_ROW convention we have to produce a flag cube flagged
		// in the planes corresponding to the he rows that have FLAG_ROW set to true
		Cube<Bool> flagCube;
		Bool flagCubeModified = False;
		flagCube = buffer_p->flagCube(); // Copy flags from input buffer
		for (size_t row_i =0;row_i<rowflags.size();row_i++)
		{
			if (rowflags(row_i))
			{
				flagCubeModified = True;
				flagCube.xyPlane(row_i) = True;
			}
		}

		if (flagCubeModified)
		{
			Cube<Bool> expandedFlagCube;
			propagateChanAvgFlags(flagCube,expandedFlagCube);
			manager_p->getVisIter()->writeFlag(expandedFlagCube);
		}
	}

	return;
}

// -----------------------------------------------------------------------
// Utility method to propagate the flags for the channel average case
// -----------------------------------------------------------------------
void MSTransformIterator::propagateChanAvgFlags (const Cube<Bool> &avgFlagCube, Cube<Bool> &expandedFlagCube)
{
	// Get original shape
	IPosition inputShape = manager_p->getVisBuffer()->getShape();
	size_t nCorr = inputShape(0);
	size_t nChan = inputShape(1);
	size_t nRows = inputShape(2);

	// Get transformed shape
	IPosition transformedShape = manager_p->getShape();
	size_t nTransChan = transformedShape(1);

	// Reshape flag cube to match the input shape
	expandedFlagCube.resize(inputShape,False);
	expandedFlagCube = False;

	// Map input-output channel
	uInt binCounts = 0;
	uInt transformedIndex = 0;
	Vector<uInt> inputOutputChan(nChan);
	uInt spw = manager_p->getVisBuffer()->spectralWindows()[0];
	uInt chanbin = manager_p->freqbinMap_p[spw];
	for (size_t chan_i =0;chan_i<nChan;chan_i++)
	{
		binCounts += 1;

		if (binCounts > chanbin)
		{
			binCounts = 1;
			transformedIndex += 1;
		}

		inputOutputChan(chan_i) = transformedIndex;
	}

	// Propagate chan-avg flags
	uInt outChan;
	for (size_t row_i =0;row_i<nRows;row_i++)
	{
		for (size_t chan_i =0;chan_i<nChan;chan_i++)
		{
			outChan = inputOutputChan(chan_i);
			if (outChan < nTransChan) // outChan >= nChan  may happen when channels are dropped
			{
				for (size_t corr_i =0;corr_i<nCorr;corr_i++)
				{
					expandedFlagCube(corr_i,chan_i,row_i) = avgFlagCube(corr_i,outChan,row_i);
				}
			}
		}
	}

	return;
}

// -----------------------------------------------------------------------
// Utility method to calculate FLAG_ROW from flag cube with the applicable convention
// -----------------------------------------------------------------------
void MSTransformIterator::calculateFlagRow (const Cube<Bool> &flagCube, Vector<Bool> &flagRow)
{
	// Get original shape
	IPosition shape = flagCube.shape();
	size_t nCorr = shape(0);
	size_t nChan = shape(1);
	size_t nRows = shape(2);

	// Reshape flag cube to match the input shape
	flagRow.resize(nRows,False);
	flagRow = False;

	Bool rowFlagValue = False;
	for (size_t row_i =0;row_i<nRows;row_i++)
	{
		rowFlagValue = True;
		for (size_t chan_i =0;chan_i<nChan;chan_i++)
		{
			if (rowFlagValue)
			{
				for (size_t corr_i =0;corr_i<nCorr;corr_i++)
				{
					if (not flagCube(corr_i,chan_i,row_i))
					{
						rowFlagValue = False;
						break;
					}
				}
			}
			else
			{
				break;
			}
		}
		flagRow(row_i) = rowFlagValue;
	}

	return;
}


} //# NAMESPACE CASA - END


