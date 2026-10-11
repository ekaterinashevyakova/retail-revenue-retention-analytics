(tableName as text, columnTypes as list) as table =>
let
    Path = Text.TrimEnd(DataFolder, {"/", "\"}) & "/" & tableName & ".csv",
    Source = Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Expected = List.Transform(columnTypes, each _{0}),
    Checked = if List.Sort(Table.ColumnNames(Headers)) = List.Sort(Expected)
              then Headers else error "Unexpected columns in " & tableName,
    Typed = Table.TransformColumnTypes(Checked, columnTypes, "en-GB")
in
    Typed
