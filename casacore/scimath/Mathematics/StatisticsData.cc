//# Copyright (C) 2000,2001
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

#include <scimath/Mathematics/StatisticsData.h>

#include <casa/Exceptions/Error.h>

namespace casa {

	String StatisticsData::toString(STATS stat) {
		switch(stat) {
		case MAX:
			return "max";
		case MEAN:
			return "mean";
		case MIN:
			return "min";
		case NPTS:
			return "npts";
		//case QUANTILE:
		//	return "quantile";
		case RMS:
			return "rms";
		case STDDEV:
			return "stddev";
		case SUM:
			return "sum";
		case SUMSQ:
			return "sumsq";
		case SUMWEIGHTS:
			return "sumOfWeights";
		case VARIANCE:
			return "variance";
		default:
			ThrowCc(
				"Logic error: Unhandled value in switch statement"
					+ String::toString(stat)
			);
		}
	}
}