# -*- coding: utf-8 -*-
# Copyright © 2023-present Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import re
import statistics
from typing import Dict, Any, Optional, List
from uim.utils.analyser import ModelAnalyzer, safe_zero_div, as_strided_array
from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.ink import InkModel, InkTree, logger
from uim.model.inkdata.strokes import Stroke, Style
from uim.model.inkinput.inputdata import InputContext, Environment, SensorContext, InputDevice, \
    InkInputProvider
from uim.model.inkinput.sensordata import SensorData
from uim.model.semantics.node import StrokeGroupNode
from uim.model.semantics.structures import BoundingBox
from uim.model.semantics.schema import TripleStore


class StatisticsAnalyzer(ModelAnalyzer):
    """
    Statistics analyzer
    ===================
    Analyze the model and compute statistics.
    """

    @staticmethod
    def merge_stats(*stats):
        """
        Merge stats.

        Parameters
        ----------
        stats: Tuple[Dict[str, Any]]
            Stats to merge.
        """

    @staticmethod
    def summarize(stats: Dict[str, Any], verbose: bool = False):
        """
        Summarize stats.

        Parameters
        ----------
        stats: Dict[str, Any]
            Stats to summarize.
        verbose: bool
            Verbose mode.
        """

    @staticmethod
    def analyze(model: InkModel, ignore_predicates: Optional[List[str]] = None,
                ignore_properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze the model and compute statistics.
        Parameters
        ----------
        model: InkModel
            Ink model to analyze.
        ignore_predicates: Optional[List[str]]
            List of predicates to ignore.
        ignore_properties: Optional[List[str]]
            List of properties to ignore.

        Returns
        -------
        stats: Dict[str, Any]
            The computed statistics.

        Raises
        ------
        StatisticsError
            If an error occurs while analyzing the model.
        """
        # Init stats
        stats: Dict[str, Any] = {
            "envs": {}, "input_devices": {}, "input_providers": {}, "brushes": {},
            "properties": StatisticsAnalyzer.__extract_properties_info(model, ignore_properties),
            "sampling_rate": StatisticsAnalyzer.__detect_sampling_rate__(model),
            "document_bounds": StatisticsAnalyzer.__compute_document_bounds__(model),
            "sensor_channels": {},
            "knowledge_graph": {},
            "points_count": {
                'stroke_points': [],
                'total': 0
            },
            "views": {},
            "uim_version": f"{model.version.major}.{model.version.minor}.{model.version.patch}",
            "strokes_count": len(model.strokes)
        }
        # Preload stats items
        StatisticsAnalyzer.__preload_stats_items__(model, stats)
        # Extract stats
        for stroke in model.strokes:
            # Extract stroke info
            StatisticsAnalyzer.__extract_stroke_info__(stroke, stats)
            # Extract input configuration
            StatisticsAnalyzer.__extract_input_configuration__(model, stroke, stats)
            # Extract sensor data info
            StatisticsAnalyzer.__extract_sensor_data_info__(model, stroke, stats)
            # Extract brush info
            StatisticsAnalyzer.__extract_brushes_information__(stroke, stats)
        # Post process stats
        StatisticsAnalyzer.__post_process_sensor_channels_info__(stats)
        # Extract views info
        StatisticsAnalyzer.__extract_views_info__(model, stats, ignore_predicates)
        # Extract knowledge graph info
        StatisticsAnalyzer.__extract_kg_info__(model, stats, ignore_predicates)
        # Post process stats
        StatisticsAnalyzer.__post_process_stats__(stats)
        return stats

    @staticmethod
    def __extract_stroke_info__(stroke: Stroke, stats: Dict[str, Any]):
        """
        Extracts stroke information from the given stroke and updates the given stats dictionary.

        Parameters
        ----------
        stroke: Stroke
            The stroke to extract information from
        stats: Dict[str, Any]
            The stats dictionary to update.
        """
        stats['points_count']['stroke_points'].append(stroke.points_count)
        stats['points_count']['total'] += stroke.points_count

    @staticmethod
    def __extract_properties_info(model: InkModel, ignore_properties: Optional[List[str]] = None):
        """
        Extracts properties information from the given model.

        Parameters
        ----------
        model: InkModel
            The model to extract information from.
        ignore_properties: Optional[List[str]]
            A list of regular expressions to ignore properties that match them.
        """
        props: Dict[str, Any] = dict(model.properties)
        result: Dict[str, Any] = {}

        for prop, value in props.items():
            should_ignore: bool = False
            if ignore_properties:
                for ip in ignore_properties:
                    if re.compile(ip).match(prop):
                        should_ignore = True
                        break
            if not should_ignore:
                if prop not in result:
                    result[prop] = {'documents_count': 0, 'values': {}}
                if value not in result[prop]['values']:
                    result[prop]['values'][value] = {"count": 0}

                result[prop]['values'][value]['count'] += 1

        return result

    @staticmethod
    def __post_process_stats__(stats: Dict[str, Any]):
        """
        Post-process the given stats dictionary.

        Parameters
        ----------
        stats: Dict[str, Any]
            The stats dictionary to post-process.
        """
        strokes_count: int = stats['strokes_count']

        for stat_type in ('brushes', 'envs', 'input_devices'):
            for k, v in stats[stat_type].items():
                stats[stat_type][k]['percent'] = round(safe_zero_div(v['strokes_count'], strokes_count) * 100, 2)

        for k, v in stats['input_providers'].items():
            stats['input_providers'][k]['percent'] = round(safe_zero_div(v['strokes_count'], strokes_count) * 100, 2)

            if 'sampling_rates' in v and len(v['sampling_rates']):
                stats['input_providers'][k]['sampling_rate'] = round(statistics.mean(v['sampling_rates']), 2)
                del stats['input_providers'][k]['sampling_rates']
            else:
                stats['input_providers'][k]['sampling_rate'] = 0

        for name, view in stats['views'].items():
            for k, v in view['leaf_classes'].items():
                stats['views'][name]['leaf_classes'][k]['percent'] = round(
                    safe_zero_div(v['strokes_count'], strokes_count) * 100, 2)

        for k, v in stats['properties'].items():
            for vk, vv in v['values'].items():
                stats['properties'][k]['values'][vk]['percent'] = round(
                    safe_zero_div(vv['count'], v['documents_count']) * 100, 2)

        for k, v in stats['sensor_channels'].items():
            stats['sensor_channels'][k]['percent'] = round(safe_zero_div(v['strokes_count'], strokes_count) * 100, 2)

        # Stroke stats
        if len(stats['points_count']['stroke_points']) > 0:
            stats['points_count']['min'] = min(stats['points_count']['stroke_points'])
            stats['points_count']['max'] = max(stats['points_count']['stroke_points'])
            stats['points_count']['mean'] = round(statistics.mean(stats['points_count']['stroke_points']), 2)
            stats['points_count']['std'] = round(statistics.stdev(stats['points_count']['stroke_points']), 2)
            stats['points_count']['median'] = round(statistics.median(stats['points_count']['stroke_points']), 2)
        else:
            stats['points_count']['min'] = 0
            stats['points_count']['max'] = 0
            stats['points_count']['mean'] = 0
            stats['points_count']['std'] = 0
            stats['points_count']['median'] = 0
        del stats['points_count']['stroke_points']

    @staticmethod
    def __preload_stats_items__(model: InkModel, stats: Dict[str, Any]):
        for env in model.input_configuration.environments:
            env_props: Dict[str, Any] = dict(env.properties)

            stats['envs'][f'env-{env.id}'] = env_props
            stats['envs'][f'env-{env.id}']['strokes_count'] = 0
            if 'user.agent' in env_props:
                rest = env_props['user.agent']
                try:
                    stats['envs'][f'env-{env.id}']['platform.name'] = rest['platform']['name']
                    stats['envs'][f'env-{env.id}']['platform.version'] = rest['platform']['version']
                    stats['envs'][f'env-{env.id}']['os.name'] = rest['os']['name']
                except Exception as e:
                    print(e)
                try:

                    stats['envs'][f'env-{env.id}']['browser.name'] = rest['browser']['name']
                    stats['envs'][f'env-{env.id}']['browser.version'] = rest['browser']['version']
                except Exception as _:
                    stats['envs'][f'env-{env.id}']['browser.name'] = 'unknown'
                    stats['envs'][f'env-{env.id}']['browser.version'] = 'unknown'

        for dev in model.input_configuration.devices:
            stats['input_devices'][f'dev-{dev.id}'] = {"strokes_count": 0}

        for ip in model.input_configuration.ink_input_providers:
            stats['input_providers'][f'prov-{ip.id}'] = {"strokes_count": 0, "sampling_rates": []}

        for brush in model.brushes.vector_brushes:
            stats['brushes'][brush.name] = {"strokes_count": 0}

        for brush in model.brushes.raster_brushes:
            stats['brushes'][brush.name] = {"strokes_count": 0}

        area = stats['document_bounds']['width'] * stats['document_bounds']['height']
        stats['document_stats'] = {"min_area": area, "max_area": area}

    @staticmethod
    def __extract_views_info__(model: InkModel, stats: Dict[str, Any], ignore_predicates: Optional[List[str]] = None):
        kg: TripleStore = model.knowledge_graph

        for v in model.views:
            v: InkTree = v

            view_info: Dict[str, Any] = {
                "assumed_type_predicate": ModelAnalyzer.__assume_view_type_predicate__(model, v),
                "statements_count": 0,
                "predicates": {},
                "leaf_classes": {}
            }

            if view_info["assumed_type_predicate"] != "unknown":
                enumerator: PreOrderEnumerator = PreOrderEnumerator(v.root)

                for node in enumerator:
                    # Calculate predicates per view
                    sts = kg.all_statements_for(subject=node.uri)
                    for statement in sts:
                        should_ignore = False
                        if ignore_predicates:
                            for ip in ignore_predicates:
                                if re.compile(ip).match(statement.predicate):
                                    should_ignore = True
                                    break

                        if not should_ignore:
                            if statement.predicate not in view_info["predicates"]:
                                view_info["predicates"][statement.predicate] = {"occurrence": 0}

                            view_info["predicates"][statement.predicate]["occurrence"] += 1

                    if isinstance(node, StrokeGroupNode):
                        children_types = [type(n) for n in node.children]

                        if StrokeGroupNode in children_types:
                            continue

                        sts = kg.all_statements_for(subject=node.uri, predicate=view_info["assumed_type_predicate"])
                        if len(sts) > 0:
                            sem_type = sts[0].object

                            if sem_type not in view_info["leaf_classes"]:
                                view_info["leaf_classes"][sem_type] = {"strokes_count": 0, 'percent': 0}

                            view_info["leaf_classes"][sem_type]["strokes_count"] += len(node.children)

            stats["views"][v.name] = view_info

    @staticmethod
    def __extract_kg_info__(model: InkModel, stats, ignore_predicates=None):
        kg: TripleStore = model.knowledge_graph

        stats["knowledge_graph"]["statements_count"] = len(kg.statements)
        stats["knowledge_graph"]["predicates"] = {}

        for statement in kg.statements:
            should_ignore = False
            if ignore_predicates:
                for ip in ignore_predicates:
                    if re.compile(ip).match(statement.predicate):
                        should_ignore = True
                        break

            if not should_ignore:
                if statement.predicate not in stats["knowledge_graph"]["predicates"]:
                    stats["knowledge_graph"]["predicates"][statement.predicate] = {"occurrence": 0}

                stats["knowledge_graph"]["predicates"][statement.predicate]["occurrence"] += 1

    @staticmethod
    def __extract_brushes_information__(stroke: Stroke, stats: Dict[str, Any]):
        """
        Extracting brush information.

        Parameters
        ----------
        stroke: Stroke
            The stroke to extract information from.
        stats: Dict[str, Any]
            The stats dictionary to update.
        """
        style: Style = stroke.style
        stats['brushes'][style.brush_uri]["strokes_count"] += 1

    @staticmethod
    def __extract_input_configuration__(model: InkModel, stroke: Stroke, stats):
        try:
            sd: SensorData = model.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
        except Exception as e:
            logger.error(f"Error while extracting input configuration: {e}")
            return

        ic: InputContext = model.input_configuration.get_input_context(sd.input_context_id)
        env: Environment = next(env for env in model.input_configuration.environments if env.id == ic.environment_id)
        stats['envs'][f'env-{env.id}']["strokes_count"] += 1

        sc: SensorContext = model.input_configuration.get_sensor_context(ic.sensor_context_id)
        for scc in sc.sensor_channels_contexts:
            try:
                input_device: InputDevice = next(
                    dev for dev in model.input_configuration.devices if dev.id == scc.input_device_id)
                stats['input_devices'][f'dev-{input_device.id}']["strokes_count"] += 1
            except Exception as e:
                logger.error(f"Error while extracting input configuration: {e}")

            try:
                input_provider: InkInputProvider = next(
                    prov for prov in model.input_configuration.ink_input_providers if prov.id == scc.input_provider_id)

                stats['input_providers'][f'prov-{input_provider.id}']["strokes_count"] += 1
                sr = StatisticsAnalyzer.__detect_stroke_sampling_rate(stroke, model)
                if sr:
                    stats['input_providers'][f'prov-{input_provider.id}']["sampling_rates"].append(sr)
            except Exception as e:
                logger.error(f"Error while extracting input configuration: {e}")

    @staticmethod
    def __detect_sampling_rate__(model: InkModel) -> float:
        """
        Calculates the average sampling rate of the strokes in the ink model.
        Parameters
        ----------
        model: InkModel
            The ink model to analyze

        Returns
        -------
        sampling_rate: float
            The average sampling rate of the strokes in the ink model in milliseconds.
        """

        per_stroke_sampling: List[float] = []

        for stroke in model.strokes:
            try:
                sr = StatisticsAnalyzer.__detect_stroke_sampling_rate(stroke, model)
                if sr:
                    per_stroke_sampling.append(sr)
            except Exception as e:
                logger.error(f"Error while detecting sampling rate: {e}")

        if len(per_stroke_sampling) == 0:
            return 0

        return round(statistics.mean(per_stroke_sampling), 2)

    @staticmethod
    def __detect_stroke_sampling_rate(stroke: Stroke, model: InkModel) -> float:
        """
        Calculates the sampling rate of a stroke in the ink model.
        Parameters
        ----------
        stroke: Stroke
            The stroke to analyze
        model: InkModel
            The ink model to analyze

        Returns
        -------
        sampling_rate: float
            The sampling rate of the stroke in milliseconds.
        """
        layout: str = "xytp"
        pos_t: int = layout.index("t")
        stride: int = len(layout)
        stride_stroke = as_strided_array(model, stroke, layout)
        ts = stride_stroke[pos_t::stride]
        if len(ts) < 2:
            return 0.

        diffs: List[float] = [round(ts[j] - ts[j - 1], 2) for j in range(1, len(ts))]
        return statistics.mean(diffs)

    @staticmethod
    def __compute_document_bounds__(model: InkModel) -> Dict[str, float]:
        """
        Computes the bounding box of the document.

        Parameters
        ----------
        model: InkModel
            The ink model to analyze.

        Returns
        -------
        bounds: Dict[str, float]
            The bounding box of the document.
        """
        if len(model.strokes) == 0:
            return {"left": 0, "top": 0, "right": 0, "bottom": 0, "width": 0, "height": 0}

        root: StrokeGroupNode = model.ink_tree.root
        model.calculate_bounds_recursively(root)
        bounds: BoundingBox = root.group_bounding_box
        return {
            "left": round(bounds.x, 2), "right": round(bounds.x + bounds.width, 2),
            "top": round(bounds.y, 2), "bottom": round(bounds.y + bounds.height, 2),
            "width": round(bounds.width, 2), "height": round(bounds.height, 2)
        }
