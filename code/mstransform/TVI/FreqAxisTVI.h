//# FreqAxisTVI.h: This file contains the interface definition of the MSTransformManager class.
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

#ifndef FreqAxisTVI_H_
#define FreqAxisTVI_H_

// Base class
#include <msvis/MSVis/TransformingVi2.h>

// VI/VB framework
#include <msvis/MSVis/VisBuffer2.h>
#include <msvis/MSVis/VisibilityIterator2.h>

// TVI framework
#include <mstransform/TVI/UtilsTVI.h>

// Measurement Set
#include <casacore/ms/MSSel/MSSelection.h>

// NOTE: See implementation include below


namespace casa { //# NAMESPACE CASA - BEGIN

namespace vi { //# NAMESPACE VI - BEGIN

//////////////////////////////////////////////////////////////////////////
// FreqAxisTVI class
//////////////////////////////////////////////////////////////////////////

template<class T> class FreqAxisTransformEngine; // Forward declaration
template<class T> class FreqAxisTransformEngine2; // Forward declaration

class FreqAxisTVI : public TransformingVi2
{

public:

	// Lifecycle
	FreqAxisTVI(ViImplementation2 * inputVii,const Record &configuration);
	~FreqAxisTVI();

	// Navigation methods
	virtual void origin ();
	virtual void next ();

	// General TVI info (common for all sub-classes)
    Bool existsColumn (VisBufferComponent2 id) const;
    Bool flagCategoryExists () const {return False;}

	// List of methods that should be implemented by derived classes
    // virtual void flag(Cube<Bool>& flagCube) const = 0;
    // virtual void floatData (Cube<Float> & vis) const = 0;
    // virtual void visibilityObserved (Cube<Complex> & vis) const = 0;
    // virtual void visibilityCorrected (Cube<Complex> & vis) const = 0;
    // virtual void visibilityModel (Cube<Complex> & vis) const = 0;
    // virtual void weightSpectrum(Cube<Float> &weightSp) const = 0;
    // virtual void sigmaSpectrum (Cube<Float> &sigmaSp) const = 0;
    // virtual Vector<Double> getFrequencies (	Double time, Int frameOfReference,Int spectralWindowId, Int msId) const = 0;
    // virtual void writeFlag (const Cube<Bool> & flagCube) = 0;

    // Common transformation for all sub-classes
    void writeFlagRow (const Vector<Bool> & flag);
    Vector<Int> getChannels (	Double time, Int frameOfReference,
    							Int spectralWindowId, Int msId) const;
    void flagRow (Vector<Bool> & flagRow) const;
    void weight (Matrix<Float> & weight) const;
    void sigma (Matrix<Float> & sigma) const;

protected:

    // Method implementing main loop  (with auxiliary data)
	template <class T> void transformFreqAxis(	Cube<T> const &inputDataCube,
												Cube<T> &outputDataCube,
												FreqAxisTransformEngine<T> &transformer) const
	{
		// Re-shape output data cube
		outputDataCube.resize(getVisBufferConst()->getShape(),False);

		// Get data shape for iteration
		const IPosition &inputShape = inputDataCube.shape();
		uInt nRows = inputShape(2);
		uInt nCorrs = inputShape(0);

		// Initialize input-output planes
		Matrix<T> inputDataPlane;
		Matrix<T> outputDataPlane;

		// Initialize input-output vectors
		Vector<T> inputDataVector;
		Vector<T> outputDataVector;

		for (uInt row=0; row < nRows; row++)
		{
			// Assign input-output planes by reference
			transformer.setRowIndex(row);
			inputDataPlane.reference(inputDataCube.xyPlane(row));
			outputDataPlane.reference(outputDataCube.xyPlane(row));

			for (uInt corr=0; corr < nCorrs; corr++)
			{
				// Assign input-output vectors by reference
				transformer.setCorrIndex(corr);
				inputDataVector.reference(inputDataPlane.row(corr));
				outputDataVector.reference(outputDataPlane.row(corr));

				// Transform data
				transformer.transform(inputDataVector,outputDataVector);
			}
		}

		return;
	}

    // Method implementing main loop  (with auxiliary data)
	template <class T> void transformFreqAxis2(	const IPosition &inputShape,
												FreqAxisTransformEngine2<T> &transformer,
												Int parallelCorrAxis=-1) const
	{
		uInt nRows = inputShape(2);
		if (parallelCorrAxis >= 0)
		{
			for (uInt row=0; row < nRows; row++)
			{
				transformer.setRowIndex(row);
				transformer.setCorrIndex(parallelCorrAxis);
				transformer.transform();
			}
		}
		else
		{
			uInt nCorrs = inputShape(0);
			for (uInt row=0; row < nRows; row++)
			{
				transformer.setRowIndex(row);

				for (uInt corr=0; corr < nCorrs; corr++)
				{
					transformer.setCorrIndex(corr);

					// jagonzal: Debug code
					/*
					VisBuffer2 *vb = getVii()->getVisBuffer();
					if (vb->rowIds()(row)==0 and corr==0)
					{
						transformer.setDebug(True);
					}
					else
					{
						transformer.setDebug(False);
					}
					*/

					transformer.transform();
				}
			}
		}

		return;
	}

	Bool parseConfiguration(const Record &configuration);
	void initialize();

	// Form spwInpChanIdxMap_p via calls to underlying Vii
	void formSelectedChanMap();

	String spwSelection_p;
	mutable LogIO logger_p;
	mutable map<Int,uInt > spwOutChanNumMap_p; // Must be accessed from const methods
	mutable map<Int,vector<Int> > spwInpChanIdxMap_p; // Must be accessed from const methods
};

//////////////////////////////////////////////////////////////////////////
// FreqAxisTransformEngine class
//////////////////////////////////////////////////////////////////////////

template<class T> class FreqAxisTransformEngine
{

public:

	virtual void transform(	Vector<T> &,Vector<T> &) {};
	virtual void setRowIndex(uInt row) {row_p = row;}
	virtual void setCorrIndex(uInt corr) {corr_p = corr;}

protected:

	uInt row_p;
	uInt corr_p;

};

//////////////////////////////////////////////////////////////////////////
// FreqAxisTransformEngine2 class
//////////////////////////////////////////////////////////////////////////

template<class T> class FreqAxisTransformEngine2
{

public:

	FreqAxisTransformEngine2(DataCubeMap *inputData,DataCubeMap *outputData)
	{
		debug_p = False;
		inputData_p = inputData;
		outputData_p = outputData;
	}

	void setRowIndex(uInt row)
	{
		rowIndex_p = row;
		inputData_p->setMatrixIndex(row);
		outputData_p->setMatrixIndex(row);

		return;
	}

	void setCorrIndex(uInt corr)
	{
		corrIndex_p = corr;
		inputData_p->setVectorIndex(corr);
		outputData_p->setVectorIndex(corr);

		return;
	}

	void setDebug(Bool debug) { debug_p = debug;}

	virtual void transform() {}

protected:

	Bool debug_p;
	uInt rowIndex_p;
	uInt corrIndex_p;
	DataCubeMap *inputData_p;
	DataCubeMap *outputData_p;

};

} //# NAMESPACE VI - END

} //# NAMESPACE CASA - END

#endif /* FreqAxisTVI_H_ */

