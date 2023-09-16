In this example, we will write a empty Analyzer. The Analyzer returns nothing and does nothing.

Full example and more details can be found in [duetector_emptyanalyzer](./duetector_emptyanalyzer/)

## 1 Write a Analyzer

Here we write the echo Analyzer and set it to not `disabled` by defaylt.

```python
class EmptyAnalyzer(Analyzer):
    def get_all_tracers(self) -> List[str]:
        """
        Get all tracers from storage.

        Returns:
            List[str]: List of tracer's name.
        """
        return []

    def get_all_collector_ids(self) -> List[str]:
        """
        Get all collector id from storage.

        Returns:
            List[str]: List of collector id.
        """
        return []

    def query(
        self,
        tracers: Optional[List[str]] = None,
        collector_ids: Optional[List[str]] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        start: int = 0,
        limit: int = 0,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        distinct: bool = False,
        order_by_asc: Optional[List[str]] = None,
        order_by_desc: Optional[List[str]] = None,
    ) -> List[Tracking]:
        """
        Query all tracking records from database.

        Args:
            tracers (Optional[List[str]], optional): Tracer's name. Defaults to None, all tracers will be queried.
            collector_ids (Optional[List[str]], optional): Collector id. Defaults to None, all collector id will be queried.
            start_datetime (Optional[datetime], optional): Start time. Defaults to None.
            end_datetime (Optional[datetime], optional): End time. Defaults to None.
            start (int, optional): Start index. Defaults to 0.
            limit (int, optional): Limit of records. Defaults to 20. ``0`` means no limit.
            columns (Optional[List[str]], optional): Columns to query. Defaults to None, all columns will be queried.
            where (Optional[Dict[str, Any]], optional): Where clause. Defaults to None.
            distinct (bool, optional): Distinct. Defaults to False.
            order_by_asc (Optional[List[str]], optional): Order by asc. Defaults to None.
            order_by_desc (Optional[List[str]], optional): Order by desc. Defaults to None.
        Returns:
            List[duetector.analyzer.models.Tracking]: List of tracking records.
        """
        return []

    def brief(
        self,
        tracers: Optional[List[str]] = None,
        collector_ids: Optional[List[str]] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        with_details: bool = True,
        distinct: bool = False,
        inspect_type: bool = False,
    ) -> AnalyzerBrief:
        """
        Get a brief of this analyzer.

        Args:
            tracers (Optional[List[str]], optional):
                Tracers. Defaults to None, all tracers will be queried.
                If a specific tracer is not found, it will be ignored.
            collector_ids (Optional[List[str]], optional):
                Collector ids. Defaults to None, all collector ids will be queried.
                If a specific collector id is not found, it will be ignored.
            start_datetime (Optional[datetime], optional): Start time. Defaults to None.
            end_datetime (Optional[datetime], optional): End time. Defaults to None.
            with_details (bool, optional): With details. Defaults to True.
            distinct (bool, optional): Distinct. Defaults to False.
            inspect_type (bool, optional): Weather fileds's value is type or type name. Defaults to False, type name.

        Returns:
            AnalyzerBrief: A brief of this analyzer.
        """
        return AnalyzerBrief(tracers=set(), collector_ids=set(), briefs={})

    def analyze(self):
        # TODO: Not design yet.
        pass


```

## 2 Register the Analyzer

```python
from duetector.extension.analyzer import hookimpl

@hookimpl
def init_analyzer(config):
    return EmptyAnalyzer(config)

```

## 3 Turning the Analyzer into a package

Here we use `pyproject.toml` as the configuration file.

```toml
# Build with hatch, you can use any build tool you like.
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "duetector-emptyanalyzer"

dependencies = ["duetector"]
dynamic = ["version"]

# This is the entry point for the AnalyzerManager to find the Analyzer.
[project.entry-points."duetector.analyzer"]
emptyanalyzer= "duetector_emptyanalyzer.empty"

[tool.hatch.version]
path = "duetector_emptyanalyzer/__init__.py"

```

## 4 Verification

Simply run the following code to verify the Analyzer is registered.

```python
from duetector.manager import AnalyzerManager
from duetector_emptyanalyzer.empty import EmptyAnalyzer


assert EmptyAnalyzer in (type(a) for a in AnalyzerManager().init())
```

## 5 Configuration

In `config.toml` you can set the Analyzer to be disabled.

```toml
[analyzer.EmptyAnalyzer]
disabled = true
```
