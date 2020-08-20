#pragma once

#include <llvm/ADT/StringRef.h>

#include <memory>
#include <string>

namespace clang {
class DeclContext;
class EnumDecl;
class NamespaceDecl;
class RecordDecl;
class Sema;
class TypeDecl;
} // namespace clang
namespace llvm {
class raw_ostream;
} // namespace llvm

namespace genpybind {
class AnnotatedEnumDecl;
class AnnotatedNamedDecl;
class AnnotatedNamespaceDecl;
class AnnotatedRecordDecl;
class AnnotationStorage;
class DeclContextGraph;

std::string getFullyQualifiedName(const clang::TypeDecl *decl);

void emitSpelling(llvm::raw_ostream &os,
                  const AnnotatedNamedDecl *annotated_decl);

class TranslationUnitExposer {
  clang::Sema &sema;
  const DeclContextGraph &graph;
  AnnotationStorage &annotations;

public:
  TranslationUnitExposer(clang::Sema &sema, const DeclContextGraph &graph,
                         AnnotationStorage &annotations);

  void emitModule(llvm::raw_ostream &os, llvm::StringRef name);
};

class DeclContextExposer {
public:
  virtual ~DeclContextExposer() = default;

  static std::unique_ptr<DeclContextExposer>
  create(const DeclContextGraph &graph, const AnnotationStorage &annotations,
         const clang::DeclContext *decl_context);

  virtual void emitDeclaration(llvm::raw_ostream &os) = 0;
  virtual void emitIntroducer(llvm::raw_ostream &os,
                              llvm::StringRef parent_identifier) = 0;
  virtual void emitDefinition(llvm::raw_ostream &os) = 0;
};

class UnnamedContextExposer : public DeclContextExposer {
public:
  UnnamedContextExposer(const clang::DeclContext *decl);

  void emitDeclaration(llvm::raw_ostream &os) override;
  void emitIntroducer(llvm::raw_ostream &os,
                      llvm::StringRef parent_identifier) override;
  void emitDefinition(llvm::raw_ostream &os) override;
};

class NamespaceExposer : public DeclContextExposer {
  const AnnotatedNamespaceDecl *annotated_decl;

public:
  NamespaceExposer(const AnnotationStorage &annotations,
                   const clang::NamespaceDecl *decl);

  void emitDeclaration(llvm::raw_ostream &os) override;
  void emitIntroducer(llvm::raw_ostream &os,
                      llvm::StringRef parent_identifier) override;
  void emitDefinition(llvm::raw_ostream &os) override;
};

class EnumExposer : public DeclContextExposer {
  const AnnotatedEnumDecl *annotated_decl;

public:
  EnumExposer(const AnnotationStorage &annotations,
              const clang::EnumDecl *decl);

  void emitDeclaration(llvm::raw_ostream &os) override;
  void emitIntroducer(llvm::raw_ostream &os,
                      llvm::StringRef parent_identifier) override;
  void emitDefinition(llvm::raw_ostream &os) override;

private:
  void emitType(llvm::raw_ostream &os);
};

class RecordExposer : public DeclContextExposer {
  const DeclContextGraph &graph;
  const AnnotatedRecordDecl *annotated_decl;

public:
  RecordExposer(const DeclContextGraph &graph,
                const AnnotationStorage &annotations,
                const clang::RecordDecl *decl);

  void emitDeclaration(llvm::raw_ostream &os) override;
  void emitIntroducer(llvm::raw_ostream &os,
                      llvm::StringRef parent_identifier) override;
  void emitDefinition(llvm::raw_ostream &os) override;

private:
  void emitType(llvm::raw_ostream &os);
};

} // namespace genpybind
