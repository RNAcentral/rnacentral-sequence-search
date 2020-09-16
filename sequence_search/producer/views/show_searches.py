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
        searches_per_month_result = []
        for row in searches_per_month_records:
            row_as_dict = dict(row)
            period = str(row_as_dict['submitted_month'].strftime("%Y-%m"))
            if period == "2020-05":
                # Remove 525 searches due to a bug in the batch search
                searches_per_month_result.append({period: row_as_dict['count'] - 525})
            elif period == "2020-06":
                # Add 50 searches that were performed in the test environment
                searches_per_month_result.append({period: row_as_dict['count'] + 50})
            else:
                searches_per_month_result.append({period: row_as_dict['count']})

        expert_dbs = ["rnacentral.org", "rfam", "mirbase", "scottgroup"]
        expert_db_results = []
        for db in expert_dbs:
            searches_per_db = await conn.execute(
                "SELECT date_trunc('month', submitted) AS submitted_month, count(id) FROM jobs "
                "WHERE (description !='sequence-search-test' OR description IS NULL) AND url LIKE %s "
                "GROUP BY submitted_month "
                "ORDER BY submitted_month",
                "%"+db+"%"
            )
            searches_per_db_records = await searches_per_db.fetchall()
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

            expert_db_results.append({expert_db: searches_per_db_list})

        response = {
            "all_searches_result": all_searches_result[0],
            "last_24_hours_result": last_24_hours_result[0],
            "last_week_result": last_week_result[0],
            "searches_per_month": searches_per_month_result,
            "expert_db_results": expert_db_results
        }

        return web.json_response(response)
