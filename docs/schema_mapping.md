# Schema mapping

Gerado a partir dos cabecalhos reais dos CSVs em `data/raw/stackoverflow/`.

Ano | Campo original | Campo padronizado
--- | --- | ---
2022 | ResponseId | respondent_id
2022 | OpSysProfessional use | operating_system
2022 | Country | country
2022 | Age | age
2022 | Employment | employment
2022 | DevType | developer_type
2022 | YearsCodePro | professional_experience
2023 | ResponseId | respondent_id
2023 | OpSysProfessional use | operating_system
2023 | Country | country
2023 | Age | age
2023 | Employment | employment
2023 | DevType | developer_type
2023 | YearsCodePro | professional_experience
2024 | ResponseId | respondent_id
2024 | OpSysProfessional use | operating_system
2024 | Country | country
2024 | Age | age
2024 | Employment | employment
2024 | DevType | developer_type
2024 | YearsCodePro | professional_experience
2025 | ResponseId | respondent_id
2025 | OpSysProfessional use | operating_system
2025 | Country | country
2025 | Age | age
2025 | Employment | employment
2025 | DevType | developer_type
2025 | WorkExp | professional_experience

Observacao: campos opcionais nao identificados permanecem nulos no dataset analitico; campos obrigatorios interrompem a transformacao.

`YearsCodePro` nao existe no survey 2025. Para 2025 foi usado `WorkExp`, que existe no schema real. `YearsCode` tambem existe, mas representa experiencia geral de codigo e nao foi tratado como equivalente direto de experiencia profissional.