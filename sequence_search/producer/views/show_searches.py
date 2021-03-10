"""
Copyright [2009-2019] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import datetime
from aiohttp import web


def convert_average_time(records):
    result = []
    for row in records:
        item = dict(row.items())
        item['avg_time'] = str(datetime.timedelta(seconds=int(item['avg_time'].seconds))) if item['avg_time'] else 0
        result.append(item)
    return result


async def show_searches(request):
    async with request.app['engine'].acquire() as conn:
        all_searches = await conn.execute(
            "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs "
            "WHERE description !='sequence-search-test' OR description IS NULL"
        )
        all_searches_records = await all_searches.fetchall()
        all_searches_result = convert_average_time(all_searches_records)

        last_24_hours = await conn.execute(
            "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs "
            "WHERE (description !='sequence-search-test' OR description IS NULL) AND submitted > %s",
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
        last_24_hours_records = await last_24_hours.fetchall()
        last_24_hours_result = convert_average_time(last_24_hours_records)

        last_week = await conn.execute(
            "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs "
            "WHERE (description !='sequence-search-test' OR description IS NULL) AND submitted > %s",
            datetime.datetime.now() - datetime.timedelta(days=7)
        )
        last_week_records = await last_week.fetchall()
        last_week_result = convert_average_time(last_week_records)

        searches_per_month = await conn.execute(
            "SELECT date_trunc('month', submitted) AS submitted_month, count(id) FROM jobs "
            "WHERE (description !='sequence-search-test' OR description IS NULL) "
            "GROUP BY submitted_month "
            "ORDER BY submitted_month",
        )
        searches_per_month_records = await searches_per_month.fetchall()

        # Old searches was delete to save space.
        # For this reason, the number of searches from Nov/2019 to Dez/20 is hardcoded.
        searches_per_month_result = [
            {"2019-11": 550}, {"2019-12": 1278}, {"2020-01": 1110}, {"2020-02": 602}, {"2020-03": 1142},
            {"2020-04": 918}, {"2020-05": 2003}, {"2020-06": 1218}, {"2020-07": 2899}, {"2020-08": 3210},
            {"2020-09": 4138}, {"2020-10": 8435}, {"2020-11": 3521}, {"2020-12": 18267}
        ]

        for row in searches_per_month_records:
            row_as_dict = dict(row)
            period = str(row_as_dict['submitted_month'].strftime("%Y-%m"))
            if period == "2021-03":
                # Add 135 searches that were performed in the test environment
                searches_per_month_result.append({period: row_as_dict['count'] + 135})
            else:
                searches_per_month_result.append({period: row_as_dict['count']})

        rnacentral_searches = [
            {"2020-05": 1116}, {"2020-06": 613}, {"2020-07": 850}, {"2020-08": 1584}, {"2020-09": 2263},
            {"2020-10": 1435}, {"2020-11": 900}, {"2020-12": 672}
        ]
        rfam_searches = [
            {"2020-05": 1313}, {"2020-06": 540}, {"2020-07": 1611}, {"2020-08": 1010}, {"2020-09": 1005},
            {"2020-10": 1292}, {"2020-11": 1806}, {"2020-12": 1340}
        ]
        mirbase_searches = [
            {"2020-07": 351}, {"2020-08": 614}, {"2020-09": 827}, {"2020-10": 529}, {"2020-11": 497},
            {"2020-12": 849}
        ]
        snodb_searches = [
            {"2020-07": 74}, {"2020-08": 0}, {"2020-09": 32}, {"2020-10": 11}, {"2020-11": 69}, {"2020-12": 4}
        ]
        gtrnadb_searches = [{"2020-11": 60}, {"2020-12": 26}]

        expert_dbs = ["rnacentral.org", "rfam", "mirbase", "scottgroup", "gtrnadb", ""]
        expert_db_results = []
        for db in expert_dbs:
            searches_per_db = await conn.execute(
                "SELECT date_trunc('month', submitted) AS submitted_month, count(id) FROM jobs "
                "WHERE (description !='sequence-search-test' OR description IS NULL) AND url LIKE %s "
                "GROUP BY submitted_month "
                "ORDER BY submitted_month",
                "%"+db+"%" if db != "" else ""
            )
            searches_per_db_records = await searches_per_db.fetchall()
            if db == "rnacentral.org":
                expert_db = "RNAcentral"
                searches_per_db_list = rnacentral_searches
            elif db == "rfam":
                expert_db = "Rfam"
                searches_per_db_list = rfam_searches
            elif db == "mirbase":
                expert_db = "miRBase"
                searches_per_db_list = mirbase_searches
            elif db == "scottgroup":
                expert_db = "snoDB"
                searches_per_db_list = snodb_searches
            elif db == "gtrnadb":
                expert_db = "GtRNAdb"
                searches_per_db_list = gtrnadb_searches
            elif db == "":
                expert_db = "Others"
                searches_per_db_list = []

            for row in searches_per_db_records:
                row_as_dict = dict(row)
                period = str(row_as_dict['submitted_month'].strftime("%Y-%m"))
                searches_per_db_list.append({period: row_as_dict['count']})

            if db == "rnacentral.org":
                expert_db = "RNAcentral"
            elif db == "rfam":
                expert_db = "Rfam"
            elif db == "mirbase":
                expert_db = "miRBase"
            elif db == "scottgroup":
                expert_db = "snoDB"
            elif db == "gtrnadb":
                expert_db = "GtRNAdb"
            elif db == "":
                expert_db = "Others"

            expert_db_results.append({expert_db: searches_per_db_list})

        response = {
            "all_searches_result": all_searches_result[0],
            "last_24_hours_result": last_24_hours_result[0],
            "last_week_result": last_week_result[0],
            "searches_per_month": searches_per_month_result,
            "expert_db_results": expert_db_results
        }

        return web.json_response(response)
