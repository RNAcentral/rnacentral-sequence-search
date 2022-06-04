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
        query = "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs " \
                "WHERE (description !='sequence-search-test' OR description IS NULL) "

        # number of searches and average time in the last 24 hours
        last_24_hours = await conn.execute(
            query + "AND submitted > %s", datetime.datetime.now() - datetime.timedelta(days=1)
        )
        last_24_hours_records = await last_24_hours.fetchall()
        last_24_hours_result = convert_average_time(last_24_hours_records)

        high_priority_24_hours = await conn.execute(
            query + "AND priority = 'high' AND submitted > %s", datetime.datetime.now() - datetime.timedelta(days=1)
        )
        high_priority_24_hours_records = await high_priority_24_hours.fetchall()
        high_priority_24_hours_result = convert_average_time(high_priority_24_hours_records)

        # number of searches and average time in the last 7 days
        last_week = await conn.execute(
            query + "AND submitted > %s", datetime.datetime.now() - datetime.timedelta(days=7)
        )
        last_week_records = await last_week.fetchall()
        last_week_result = convert_average_time(last_week_records)

        high_priority_last_week = await conn.execute(
            query + "AND priority = 'high' AND submitted > %s", datetime.datetime.now() - datetime.timedelta(days=7)
        )
        high_priority_last_week_records = await high_priority_last_week.fetchall()
        high_priority_last_week_result = convert_average_time(high_priority_last_week_records)

        # get data from statistic table
        searches_per_month_query = await conn.execute("SELECT period,source,total FROM statistic ORDER BY period")
        searches_per_month_records = await searches_per_month_query.fetchall()
        searches_per_month_result = []

        for row in searches_per_month_records:
            row_as_dict = dict(row)
            searches_per_month_result.append(
                {'period': row_as_dict['period'], 'source': row_as_dict['source'], 'total': row_as_dict['total']}
            )

        searches_per_month = []
        expert_db_results = [
            {"RNAcentral": []}, {"Rfam": []}, {"miRBase": []}, {"snoDB": []}, {"GtRNAdb": []},
        ]

        for elem in searches_per_month_result:
            period = elem['period']
            source = elem['source']
            total = elem['total']

            # add results in search_per_month
            if not any(period in item for item in searches_per_month):
                searches_per_month.append({period: total})
            else:
                for item in searches_per_month:
                    for key, value in item.items():
                        if key == period:
                            item[key] = value + total

            # add results in expert_db_results
            for item in expert_db_results:
                for key, value in item.items():
                    if key == source:
                        value.append({period: total})

        response = {
            "last_24_hours_result": last_24_hours_result[0],
            "last_week_result": last_week_result[0],
            "high_priority_24_hours_result": high_priority_24_hours_result[0],
            "high_priority_last_week_result": high_priority_last_week_result[0],
            "searches_per_month": searches_per_month,
            "expert_db_results": expert_db_results
        }

        return web.json_response(response)
