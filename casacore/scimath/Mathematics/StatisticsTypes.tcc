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

#include <casa/aips.h>

#include <scimath/Mathematics/StatisticsTypes.h>

#include <casa/Containers/Record.h>
#include <scimath/Mathematics/StatisticsData.h>

namespace casa {

template <class AccumType>
StatsData<AccumType> initializeStatsData() {
	StatsData<AccumType> init = {
		False,
		NULL,
		std::pair<Int64, Int64>(-1, -1),
		0,
		NULL,
		NULL,
		NULL,
		std::pair<Int64, Int64>(-1, -1),
		0,
		0,
		0,
		0,
		0,
		0,
		0,
		0,
		False
	};
	return init;
}

template <class AccumType>
StatsData<AccumType> copy(const StatsData<AccumType>& stats) {
	StatsData<AccumType> copy = stats;
	if (! copy.max.null()) {
		copy.max = new AccumType(*copy.max);
	}
	if (! copy.median.null()) {
		copy.median = new AccumType(*copy.median);
	}
	if (! copy.medAbsDevMed.null()) {
		copy.medAbsDevMed = new AccumType(*copy.medAbsDevMed);
	}
	if (! copy.min.null()) {
		copy.min = new AccumType(*copy.min);
	}
}

template <class AccumType>
Record toRecord(const StatsData<AccumType>& stats) {
	Record r;
	r.define("isMasked", stats.masked);
	r.define("isWeighted", stats.weighted);
	if (stats.weighted) {
		r.define(
			StatisticsData::toString(StatisticsData::SUMWEIGHTS),
			stats.sumweights
		);
	}
	r.define(
		StatisticsData::toString(StatisticsData::MEAN), stats.mean
	);
	r.define(
		StatisticsData::toString(StatisticsData::NPTS), stats.npts
	);
	r.define(
		StatisticsData::toString(StatisticsData::RMS), stats.rms
	);
	r.define(
		StatisticsData::toString(StatisticsData::STDDEV),
		sqrt(stats.stddev)
	);
	r.define(
		StatisticsData::toString(StatisticsData::SUM), stats.sum
	);
	r.define(
		StatisticsData::toString(StatisticsData::SUMSQ), stats.sumsq
	);
	r.define(
		StatisticsData::toString(StatisticsData::VARIANCE), stats.variance
	);
	if (! stats.max.null()) {
		r.define(
			StatisticsData::toString(StatisticsData::MAX), *stats.max
		);
		r.define("maxDatasetIndex", stats.maxpos.first);
		r.define("maxIndex", stats.maxpos.second);
	}
	if (! stats.min.null()) {
		r.define(
			StatisticsData::toString(StatisticsData::MIN), *stats.min
		);
		r.define("minDatasetIndex", stats.minpos.first);
		r.define("minIndex", stats.minpos.second);
	}
	return r;
}

}